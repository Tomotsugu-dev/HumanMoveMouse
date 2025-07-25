#!/usr//env python3
# human_mouse_stat_mj.py
# 统计‑混合模型 ＋ Minimum‑Jerk 噪声（修正版 2025‑07‑15）
# Statistical Mixture Model + Minimum-Jerk Noise (Revised 2025-07-15)
# ----------------------------------------------------
# 依赖：numpy pandas scipy scikit-learn
# Dependencies: numpy pandas scipy scikit-learn

import argparse
import pickle
from pathlib import Path
from typing import Tuple, Optional
import inspect

import numpy as np
import pandas as pd
from scipy import interpolate
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture

# ====================================================
#                      核心类定义
#                 Core Class Definition
# ====================================================

class HumanMouseModel:
    """
    统计‑混合（PCA + GMM）鼠标轨迹生成器
    Statistical-Mixture (PCA + GMM) Mouse Trajectory Generator

    兼容 Mouse Trajectory Collector 的 CSV 格式：
    Compatible with the CSV format from Mouse Trajectory Collector:
      列名：x_coordinate  |  y_coordinate  |  time_interval_seconds
      Column names: x_coordinate | y_coordinate | time_interval_seconds
      第一个 time_interval_seconds 必须为 0
      The first time_interval_seconds must be 0
    """
    # ----------------- 构造 & 训练 ------------------
    # ----------- Constructor & Training -----------
    def __init__(self,
                 K: int = 30,
                 n_shape_pc: int = 6,
                 n_mix_shape: int = 7,
                 n_mix_global: int = 5,
                 seed: int = 42):
        """
        Args:
            K              (int): 每条轨迹按弧长重采样到 K 点
                                  Resample each trajectory to K points by arc length.
            n_shape_pc     (int): 形状 PCA 主成分个数
                                  Number of principal components for shape PCA.
            n_mix_shape    (int): 形状 GMM 混合成分数
                                  Number of mixture components for shape GMM.
            n_mix_global   (int): 全局特征 GMM 混合成分数
                                  Number of mixture components for global features GMM.
            seed           (int): 默认随机种子（训练阶段）
                                  Default random seed (for the training phase).
        """
        self.K = K
        self.n_shape_pc = n_shape_pc
        self.n_mix_shape = n_mix_shape
        self.n_mix_global = n_mix_global
        self.seed = seed

        # 训练后置属性
        # Attributes set after training
        self.pca: PCA | None = None
        self.gmm_shape: GaussianMixture | None = None
        self.gmm_global: GaussianMixture | None = None
        self._is_trained = False

        np.random.seed(seed)

    def fit(self, csv_dir: str | Path):
        """
        读取目录下全部 CSV 并训练模型
        Read all CSV files in a directory and train the model.
        """
        csv_dir = Path(csv_dir)
        xy_list, dt_list = self._load_traces(csv_dir)
        shapes, globals_ = self._extract_features(xy_list, dt_list)

        # 形状：PCA → GMM
        # Shape: PCA -> GMM
        self.pca = PCA(self.n_shape_pc, random_state=self.seed)
        coeffs = self.pca.fit_transform(shapes)
        self.gmm_shape = GaussianMixture(
            self.n_mix_shape,
            covariance_type="full",
            random_state=self.seed
        ).fit(coeffs)

        # 全局：GMM
        # Global features: GMM
        self.gmm_global = GaussianMixture(
            self.n_mix_global,
            covariance_type="full",
            random_state=self.seed
        ).fit(globals_)

        self._is_trained = True
        print(f"[Training complete] Number of trajectories: {len(xy_list)}")

    # ----------------- 生成 ------------------
    # ---------------- Generation ---------------
    def generate(self,
                 start: tuple[float, float],
                 end: tuple[float, float],
                 N: int = 120,
                 amp_jitter_px: float = 1.0,
                 seed: int | None = None
                 ) -> tuple[np.ndarray, np.ndarray]:
        """
        生成单条轨迹
        Generate a single trajectory.

        Returns
        -------
        xy_abs : (N,2)  float32  绝对坐标
                                 Absolute coordinates.
        dt     : (N,)   float32  相邻采样时间间隔（秒），dt[0]=0
                                 Time interval between adjacent samples (seconds), dt[0]=0.
        """
        if not self._is_trained:
            raise RuntimeError("Model is not trained yet. Please call fit() first.")

        # ---- RNG 统一入口 ----
        # ---- Unified entry point for RNG ----
        rs = np.random.RandomState(seed) if seed is not None else None
        rng = np.random.default_rng(seed)

        # 1) 采样形状 & 全局标量（用同一 random_state 保证可复现）
        # 1) Sample shape & global scalars (use the same random_state for reproducibility)
        coeff = self._gmm_sample(self.gmm_shape, 1, rs)[0][0].astype("float32")
        global_sample = self._gmm_sample(self.gmm_global, 1, rs)[0][0]
        D_hat, T_hat, *_ = global_sample  # 训练样本的总距离、总时间估计
                                           # Estimated total distance and time from training samples

        # 2) 形状基曲线：x 轴用 Minimum‑Jerk 位移，解决「尾段速度异常」
        # 2) Base shape curve: Use Minimum-Jerk displacement for the x-axis to fix "abnormal end-segment velocity"
        t_k = np.linspace(0, 1, self.K, dtype="float32")
        xs_k = self._min_jerk_position(t_k)              # 单调 0→1 / Monotonically increasing from 0 to 1
        shape = np.stack([xs_k, coeff @ self.pca.components_ + self.pca.mean_], axis=1)

        # 3) 插值到 N 点（x 仍为 MJ 位移）
        # 3) Interpolate to N points (x is still MJ displacement)
        spl = interpolate.CubicSpline(shape[:, 0], shape[:, 1])
        xs_N = self._min_jerk_position(np.linspace(0, 1, N, dtype="float32"))
        ys_N = spl(xs_N).astype("float32")
        traj_norm = np.stack([xs_N, ys_N], axis=1)       # 归一化轨迹 / Normalized trajectory

        # 4) Minimum‑Jerk 速度曲线 → dt
        # 4) Minimum-Jerk velocity profile -> dt
        v_w = self._min_jerk_velocity_profile(N)
        dt = (T_hat * v_w).astype("float32")
        dt = np.concatenate(([0.], dt))                  # dt[0]=0, 长度 N / length N

        # 5) 仿射映射到真实起‑终点
        # 5) Affine mapping to the real start and end points
        S, E = np.float32(start), np.float32(end)
        v_SE = E - S
        dist = np.linalg.norm(v_SE)
        theta = np.arctan2(v_SE[1], v_SE[0])
        R = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta),  np.cos(theta)]],
                     dtype="float32")
        xy_abs = (R @ (traj_norm.T * dist)).T + S        # (N,2)

        # 6) 距离‑时间自适应缩放：保持平均速度合理
        # 6) Distance-time adaptive scaling: keep the average speed reasonable
        if D_hat > 1e-3:
            xy_scale = dist / D_hat
            dt[1:] *= xy_scale

        # 7) 添加 MJ 抖动噪声（同一 RNG）
        # 7) Add MJ jitter noise (same RNG)
        noise = rng.normal(0, amp_jitter_px, xy_abs.shape).astype("float32")
        w_t = self._min_jerk_position(np.linspace(0, 1, N, dtype="float32"))
        xy_abs += w_t[:, None] * noise

        return xy_abs, dt

    @staticmethod
    def _gmm_sample(gmm, n_samples, rs=None):
        """
        对 scikit-learn < 1.2 不支持 random_state 的向后兼容封装
        Backward compatibility wrapper for scikit-learn < 1.2 which doesn't support random_state.
        返回值与 gmm.sample 相同
        Returns the same as gmm.sample.
        """
        if 'random_state' in inspect.signature(gmm.sample).parameters:
            # 新版接口，直接传
            # New interface, pass directly
            return gmm.sample(n_samples, random_state=rs)
        else:
            # 旧版接口：临时覆盖 gmm.random_state
            # Old interface: temporarily override gmm.random_state
            if rs is not None:
                old = getattr(gmm, 'random_state', None)
                gmm.random_state = rs
                out = gmm.sample(n_samples)
                gmm.random_state = old
                return out
            return gmm.sample(n_samples)

    # ----------------- 模型持久化 ------------------
    # -------------- Model Persistence --------------
    def save(self, filepath: str | Path):
        if not self._is_trained:
            raise RuntimeError("Model is not trained yet. Please call fit() first.")
        with open(filepath, "wb") as f:
            pickle.dump(self.__dict__, f)

    @classmethod
    def load(cls, filepath: str | Path) -> "HumanMouseModel":
        with open(filepath, "rb") as f:
            state = pickle.load(f)
        self = cls()
        self.__dict__.update(state)
        return self

    # ====================================================
    #                     -------- 私有工具 --------
    #                    ----- Private Utilities -----
    # ====================================================

    # ---------- 数据加载 ----------
    # ---------- Data Loading ----------
    @staticmethod
    def _load_traces(csv_dir: Path):
        """
        读取目录内全部 CSV 并做基本合法性检查
        Read all CSVs in the directory and perform basic validation.
        """
        xy_list, dt_list = [], []
        files = sorted(csv_dir.glob("*.csv"))
        if not files:
            raise ValueError(f"No CSV files found in directory {csv_dir}")

        print(f"[Loading] Found {len(files)} CSV files.")
        for fp in files:
            try:
                df = pd.read_csv(fp)

                # 必需列
                # Required columns
                cols_needed = {"x_coordinate", "y_coordinate", "time_interval_seconds"}
                if not cols_needed.issubset(df.columns):
                    print(f"[Skipping] {fp.name} is missing required columns.")
                    continue

                xy = df[["x_coordinate", "y_coordinate"]].values.astype("float32")
                dts = df["time_interval_seconds"].values.astype("float32")

                if len(xy) < 10 or len(xy) != len(dts):
                    print(f"[Skipping] {fp.name} has insufficient data points or mismatched column lengths.")
                    continue

                # 第一个 dt 应为 0，若不是则修正
                # The first dt should be 0, correct it if not.
                if abs(dts[0]) > 1e-6:
                    # 判断是否累积时间
                    # Check if it's cumulative time
                    if np.all(np.diff(dts) >= 0):
                        dts = np.concatenate(([0.], np.diff(dts)))
                    else:
                        dts[0] = 0.

                if np.any(dts[1:] <= 0):
                    print(f"[Skipping] {fp.name} contains non-positive time intervals.")
                    continue

                xy_list.append(xy)
                dt_list.append(dts)

            except Exception as e:
                print(f"[Error] Failed to read {fp.name}: {e}")

        if not xy_list:
            raise ValueError("No valid trajectories available for training.")
        print(f"[Load complete] Valid trajectories: {len(xy_list)}")
        return xy_list, dt_list

    # ---------- 特征 ----------
    # -------- Features --------
    def _extract_features(self, xy_list, dt_list):
        shapes, globals_ = [], []
        for xy, dts in zip(xy_list, dt_list):
            xy_n, dist, *_ = self._affine_normalise(xy)
            xy_rs = self._resample_by_arclength(xy_n, self.K)
            shapes.append(xy_rs[:, 1])  # 仅保存 y（形状）/ Only save y (the shape)
            globals_.append(self._global_features(xy, dts))
        return np.stack(shapes), np.stack(globals_)

    # ---------- 归一化 & 重采样 ----------
    # ----- Normalization & Resampling -----
    @staticmethod
    def _affine_normalise(xy):
        """
        仿射归一化到起点 (0,0)、终点 (1,0)
        Affine normalize to start point (0,0) and end point (1,0).
        """
        p0, pN = xy[0], xy[-1]
        v = pN - p0
        dist = np.linalg.norm(v) or 1.
        theta = -np.arctan2(v[1], v[0])
        R = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])
        xy_n = (R @ (xy - p0).T).T / dist
        return xy_n, dist, theta, p0

    @staticmethod
    def _resample_by_arclength(xy, K):
        d = np.linalg.norm(np.diff(xy, axis=0), axis=1)
        s = np.hstack(([0.], np.cumsum(d)))
        s /= s[-1] if s[-1] > 0 else 1.
        fx = interpolate.interp1d(s, xy[:, 0])
        fy = interpolate.interp1d(s, xy[:, 1])
        s_new = np.linspace(0, 1, K, dtype="float32")
        return np.stack([fx(s_new), fy(s_new)], axis=1)

    # ---------- 全局特征 ----------
    # ------- Global Features --------
    @staticmethod
    def _global_features(xy, dts):
        D = np.sum(np.linalg.norm(np.diff(xy, axis=0), axis=1))
        T = np.sum(dts)
        valid_dt = dts[1:]
        if len(valid_dt) > 0 and np.all(valid_dt > 0):
            speed = np.linalg.norm(np.diff(xy, axis=0), axis=1) / valid_dt
            mean_s, max_s = speed.mean(), speed.max()
        else:
            mean_s = max_s = D / T if T > 0 else 0.
        return np.array([D, T, mean_s, max_s], dtype="float32")

    # ---------- Minimum‑Jerk 相关 ----------
    # --------- Minimum-Jerk Related ---------
    @staticmethod
    def _min_jerk_velocity_profile(N):
        """
        长度 N‑1 的速度权重，和为 1
        Velocity weights of length N-1, summing to 1.
        """
        t_mid = (np.arange(N - 1) + 0.5) / (N - 1)
        v = 30 * t_mid ** 2 - 60 * t_mid ** 3 + 30 * t_mid ** 4
        return v / v.sum()

    @staticmethod
    def _min_jerk_position(t):
        """
        t∈[0,1] → 0‑1 的 MJ 位移
        t in [0,1] -> MJ displacement from 0 to 1.
        """
        return 10 * t ** 3 - 15 * t ** 4 + 6 * t ** 5

# ====================================================
#                       公共 API
#                       Public API
# ====================================================

def diagnose_csv_file(csv_path: str) -> None:
    """
    快速检查单个 CSV 是否满足格式要求
    Quickly check if a single CSV file meets format requirements.
    """
    df = pd.read_csv(csv_path)
    print(f"\n=== Diagnosing: {Path(csv_path).name} ===")
    print(f"Number of rows: {len(df)}")
    print(f"Column names: {list(df.columns)}")
    if "time_interval_seconds" in df.columns:
        dts = df["time_interval_seconds"].values
        print(f"First 5 dt values: {dts[:5]}")
        print(f"Min dt: {dts.min()}, Max dt: {dts.max()}")
    if {"x_coordinate", "y_coordinate"} <= set(df.columns):
        x, y = df["x_coordinate"].values, df["y_coordinate"].values
        print(f"Start ({x[0]:.1f},{y[0]:.1f}) -> End ({x[-1]:.1f},{y[-1]:.1f})")

def train_mouse_model(csv_directory: str,
                      model_save_path: str = "mouse_model.pkl",
                      **kwargs) -> None:
    model = HumanMouseModel(**kwargs)
    model.fit(csv_directory)
    model.save(model_save_path)
    print(f"[Saved] Model has been written to -> {model_save_path}")

def generate_mouse_trajectory(model_path: str,
                              start_point: Tuple[float, float],
                              end_point: Tuple[float, float],
                              num_points: int = 120,
                              jitter_amplitude: float = 1.0,
                              seed: Optional[int] = None
                              ) -> Tuple[np.ndarray, np.ndarray]:
    model = HumanMouseModel.load(model_path)
    return model.generate(start_point, end_point,
                          N=num_points,
                          amp_jitter_px=jitter_amplitude,
                          seed=seed)


# ====================================================
#                     命令行接口
#                Command-Line Interface
# ====================================================

def _cli():
    parser = argparse.ArgumentParser(
        description="HumanMouseModel Training / Generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # diagnose
    p_d = sub.add_parser("diagnose", help="Diagnose a single CSV file")
    p_d.add_argument("csv_file", help="Path to the CSV file to diagnose")

    # train
    p_t = sub.add_parser("train", help="Train a new model from a directory of CSVs")
    p_t.add_argument("csv_dir", help="Directory containing trajectory CSV files")
    p_t.add_argument("--save", default="mouse_model.pkl", help="Path to save the trained model")
    p_t.add_argument("--K", type=int, default=30, help="Number of points for resampling")
    p_t.add_argument("--n_shape_pc", type=int, default=6, help="Number of PCA components for shape")
    p_t.add_argument("--n_mix_shape", type=int, default=7, help="Number of GMM mixtures for shape")
    p_t.add_argument("--n_mix_global", type=int, default=5, help="Number of GMM mixtures for global features")

    # gen
    p_g = sub.add_parser("gen", help="Generate a trajectory from a trained model")
    p_g.add_argument("model_pkl", help="Path to the trained model .pkl file")
    p_g.add_argument("x0", type=float, help="Start point x-coordinate")
    p_g.add_argument("y0", type=float, help="Start point y-coordinate")
    p_g.add_argument("x1", type=float, help="End point x-coordinate")
    p_g.add_argument("y1", type=float, help="End point y-coordinate")
    p_g.add_argument("--num_points", type=int, default=120, help="Number of points in the generated trajectory")
    p_g.add_argument("--jitter", type=float, default=1.0, help="Amplitude of the jitter noise in pixels")
    p_g.add_argument("--seed", type=int, help="Random seed for reproducibility")
    p_g.add_argument("--out_csv", help="Optional path to save the generated trajectory as a CSV file")

    args = parser.parse_args()

    if args.cmd == "diagnose":
        diagnose_csv_file(args.csv_file)

    elif args.cmd == "train":
        train_mouse_model(
            args.csv_dir,
            args.save,
            K=args.K,
            n_shape_pc=args.n_shape_pc,
            n_mix_shape=args.n_mix_shape,
            n_mix_global=args.n_mix_global
        )

    elif args.cmd == "gen":
        xy, dt = generate_mouse_trajectory(
            args.model_pkl,
            (args.x0, args.y0),
            (args.x1, args.y1),
            num_points=args.num_points,
            jitter_amplitude=args.jitter,
            seed=args.seed
        )
        if args.out_csv:
            df = pd.DataFrame({
                "x_coordinate": xy[:, 0],
                "y_coordinate": xy[:, 1],
                "time_interval_seconds": dt
            })
            df.to_csv(args.out_csv, index=False, float_format="%.6f")
            print(f"[Saved] Trajectory written to -> {args.out_csv}")
        else:
            print("First 5 sampled points (x, y, dt):")
            for i in range(min(5, len(xy))):
                print(f"{xy[i, 0]:.1f}, {xy[i, 1]:.1f}, {dt[i]:.4f}")

if __name__ == "__main__":
    _cli()