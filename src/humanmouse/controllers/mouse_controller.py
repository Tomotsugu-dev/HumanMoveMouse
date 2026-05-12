#!/usr/bin/env python3
"""
仿真人类鼠标操作控制器
A controller for simulating human-like mouse operations.
"""
import random
import time
from typing import Optional, Tuple

import numpy as np
import pyautogui

from ..models import get_default_model_path
from ..models.trajectory_model import generate_mouse_trajectory


def _configure_pyautogui() -> None:
    """
    将 pyautogui 配置为零延迟模式(本库自己用 dt 控制节奏)。
    Configure pyautogui for zero-latency mode; this library drives timing via dt.
    """
    pyautogui.MINIMUM_DURATION = 0.0
    pyautogui.MINIMUM_SLEEP = 0.0
    pyautogui.PAUSE = 0.0


class HumanMouseController:
    """
    仿真人类鼠标操作控制器
    A controller for simulating human-like mouse operations.

    支持的操作 / Supported operations:
    - 移动后单击 / Move and click
    - 移动后双击 / Move and double-click
    - 单纯移动 / Move only
    - 移动后右击 / Move and right-click
    - 按住左键拖拽 / Drag and drop (press and hold left button)
    """

    # 直线模式下的基准速度(像素/秒);最终耗时还会被 speed_factor 进一步缩放
    # Baseline pixel/second for straight mode; further scaled by speed_factor at execution time.
    STRAIGHT_PX_PER_SEC: float = 1500.0

    def __init__(self,
                 model_pkl: Optional[str] = None,
                 num_points: int = 100,
                 jitter_amplitude: float = 0.3,
                 speed_factor: float = 1.0,
                 straight: bool = False):
        """
        初始化鼠标控制器
        Initializes the mouse controller.

        Args:
            model_pkl: 训练好的模型文件路径（必须）/ Path to the trained model file (required).
            num_points: 轨迹采样点数，默认100 / Number of points for trajectory sampling, default is 100.
            jitter_amplitude: 抖动幅度，默认0.3 / Amplitude of the jitter, default is 0.3.
            speed_factor: 速度因子，默认1.0，值越大移动越快 / Speed factor, default is 1.0, higher values mean faster movement.
            straight: 直线旁路模式，跳过 PCA/GMM 模型直接走直线 / Straight-line bypass; skips the PCA/GMM model.
        """
        # 默认走包内随包分发的模型 / Default to the model bundled with the package
        self.model_pkl: str = model_pkl if model_pkl is not None else get_default_model_path()
        self.num_points = num_points
        self.jitter_amplitude = jitter_amplitude
        self.speed_factor = speed_factor
        self.straight = straight

        _configure_pyautogui()

    def _generate_trajectory(self,
                             start_point: Tuple[float, float],
                             end_point: Tuple[float, float],
                             seed: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成鼠标轨迹
        Generates the mouse trajectory.

        Args:
            start_point: 起始坐标 (x, y) / Starting coordinates (x, y).
            end_point: 结束坐标 (x, y) / Ending coordinates (x, y).
            seed: 随机种子，默认None表示随机(直线模式忽略) / Random seed (ignored in straight mode).

        Returns:
            xy: 轨迹坐标数组 (N, 2) / Trajectory coordinate array (N, 2).
            dt: 时间间隔数组 (N,) / Time interval array (N,).
        """
        if self.straight:
            return self._straight_trajectory(start_point, end_point)

        # 如果没有指定seed，生成随机seed / If no seed is specified, generate a random one.
        if seed is None:
            seed = random.randint(0, 1000000)

        return generate_mouse_trajectory(
            model_path=self.model_pkl,
            start_point=start_point,
            end_point=end_point,
            num_points=self.num_points,
            jitter_amplitude=self.jitter_amplitude,
            seed=seed
        )

    def _straight_trajectory(self,
                             start_point: Tuple[float, float],
                             end_point: Tuple[float, float]
                             ) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成严格直线轨迹 + Minimum-Jerk 速度剖面(平滑加减速)。
        Generate a strict straight-line trajectory with a Minimum-Jerk velocity profile.

        端点严格命中 / Endpoints are exact.
        """
        start_arr = np.asarray(start_point, dtype=np.float32)
        end_arr = np.asarray(end_point, dtype=np.float32)
        xy = np.linspace(start_arr, end_arr, self.num_points, dtype=np.float32)

        dist = float(np.linalg.norm(end_arr - start_arr))
        total_t = dist / self.STRAIGHT_PX_PER_SEC

        # MJ 速度剖面:两端慢中段快,长度 N-1,总和归一 / MJ velocity profile, sums to 1
        t_mid = (np.arange(self.num_points - 1) + 0.5) / max(self.num_points - 1, 1)
        v = 30 * t_mid ** 2 - 60 * t_mid ** 3 + 30 * t_mid ** 4
        v = v / v.sum() if v.sum() > 0 else np.full_like(v, 1.0 / len(v))
        dt = np.concatenate(([0.0], v * total_t)).astype(np.float32)
        return xy, dt

    def _execute_trajectory(self, xy: np.ndarray, dt: np.ndarray):
        """
        执行鼠标轨迹移动
        Executes the mouse trajectory movement.

        Args:
            xy: 轨迹坐标数组 (N, 2) / Trajectory coordinate array (N, 2).
            dt: 时间间隔数组 (N,) / Time interval array (N,).
        """
        # 移动到第一个点（瞬间移动）/ Move to the first point (instantaneously).
        pyautogui.moveTo(xy[0, 0], xy[0, 1], duration=0)

        # 沿轨迹移动 / Move along the trajectory.
        for i in range(1, len(xy)):
            # 移动到下一个点 / Move to the next point.
            pyautogui.moveTo(xy[i, 0], xy[i, 1], duration=0)
            # 等待对应的时间间隔，根据速度因子调整 / Wait for the time interval, adjusted by speed factor.
            # 注意 dt 是 numpy.float32, Python 3.13 的 time.sleep 不接受, 必须转 float.
            # Note: dt is numpy.float32; Python 3.13's time.sleep rejects it, so cast to float.
            if dt[i] > 0:
                adjusted_delay = float(dt[i]) / self.speed_factor
                if adjusted_delay > 0:
                    time.sleep(adjusted_delay)

    def move(self,
             start_point: Tuple[float, float],
             end_point: Tuple[float, float],
             seed: Optional[int] = None):
        """
        单纯移动鼠标
        Moves the mouse only.

        Args:
            start_point: 起始坐标 (x, y) / Starting coordinates (x, y).
            end_point: 结束坐标 (x, y) / Ending coordinates (x, y).
            seed: 随机种子，默认None表示随机 / Random seed, None means random.
        """
        xy, dt = self._generate_trajectory(start_point, end_point, seed)
        self._execute_trajectory(xy, dt)

    def move_and_click(self,
                       start_point: Tuple[float, float],
                       end_point: Tuple[float, float],
                       seed: Optional[int] = None):
        """
        移动后单击
        Moves the mouse and then clicks.

        Args:
            start_point: 起始坐标 (x, y) / Starting coordinates (x, y).
            end_point: 结束坐标 (x, y) / Ending coordinates (x, y).
            seed: 随机种子，默认None表示随机 / Random seed, None means random.
        """
        # 先移动 / First, move the mouse.
        self.move(start_point, end_point, seed)
        # 短暂延迟后单击 / Click after a short delay.
        time.sleep(random.uniform(0.05, 0.15) / self.speed_factor)
        pyautogui.click()

    def move_and_double_click(self,
                              start_point: Tuple[float, float],
                              end_point: Tuple[float, float],
                              seed: Optional[int] = None):
        """
        移动后双击
        Moves the mouse and then double-clicks.

        Args:
            start_point: 起始坐标 (x, y) / Starting coordinates (x, y).
            end_point: 结束坐标 (x, y) / Ending coordinates (x, y).
            seed: 随机种子，默认None表示随机 / Random seed, None means random.
        """
        # 先移动 / First, move the mouse.
        self.move(start_point, end_point, seed)
        # 短暂延迟后双击 / Double-click after a short delay.
        time.sleep(random.uniform(0.05, 0.15) / self.speed_factor)
        pyautogui.doubleClick()

    def move_and_right_click(self,
                             start_point: Tuple[float, float],
                             end_point: Tuple[float, float],
                             seed: Optional[int] = None):
        """
        移动后右击
        Moves the mouse and then right-clicks.

        Args:
            start_point: 起始坐标 (x, y) / Starting coordinates (x, y).
            end_point: 结束坐标 (x, y) / Ending coordinates (x, y).
            seed: 随机种子，默认None表示随机 / Random seed, None means random.
        """
        # 先移动 / First, move the mouse.
        self.move(start_point, end_point, seed)
        # 短暂延迟后右击 / Right-click after a short delay.
        time.sleep(random.uniform(0.05, 0.15) / self.speed_factor)
        pyautogui.rightClick()

    def drag(self,
             start_point: Tuple[float, float],
             end_point: Tuple[float, float],
             seed: Optional[int] = None):
        """
        按住左键拖拽移动
        Drags the mouse with the left button held down.

        Args:
            start_point: 起始坐标 (x, y) / Starting coordinates (x, y).
            end_point: 结束坐标 (x, y) / Ending coordinates (x, y).
            seed: 随机种子，默认None表示随机 / Random seed, None means random.
        """
        xy, dt = self._generate_trajectory(start_point, end_point, seed)

        # 移动到起始点 / Move to the starting point.
        pyautogui.moveTo(xy[0, 0], xy[0, 1], duration=0)
        time.sleep(random.uniform(0.05, 0.1) / self.speed_factor)

        # 按下鼠标左键 / Press the left mouse button down.
        pyautogui.mouseDown()

        # 沿轨迹拖拽 / Drag along the trajectory.
        for i in range(1, len(xy)):
            pyautogui.moveTo(xy[i, 0], xy[i, 1], duration=0)
            if dt[i] > 0:
                adjusted_delay = float(dt[i]) / self.speed_factor
                if adjusted_delay > 0:
                    time.sleep(adjusted_delay)

        # 释放鼠标左键 / Release the left mouse button.
        time.sleep(random.uniform(0.05, 0.1) / self.speed_factor)
        pyautogui.mouseUp()

    def set_speed(self, speed_factor: float):
        """
        设置速度因子
        Sets the speed factor.

        Args:
            speed_factor: 新的速度因子，必须大于0 / New speed factor, must be greater than 0.
        """
        if speed_factor <= 0:
            raise ValueError("Speed factor must be greater than 0")
        self.speed_factor = speed_factor

    # ===== 新增方法：从当前位置开始移动 / New methods: move from current position =====
    
    def move_to(self, end_point: Tuple[float, float], seed: Optional[int] = None):
        """
        从当前鼠标位置移动到目标位置
        Moves from current mouse position to target position.
        
        Args:
            end_point: 目标坐标 (x, y) / Target coordinates (x, y).
            seed: 随机种子，默认None表示随机 / Random seed, None means random.
        """
        current_pos = pyautogui.position()
        self.move((current_pos.x, current_pos.y), end_point, seed)
    
    def click_at(self, end_point: Tuple[float, float], seed: Optional[int] = None):
        """
        从当前鼠标位置移动到目标位置并单击
        Moves from current mouse position to target and clicks.
        
        Args:
            end_point: 目标坐标 (x, y) / Target coordinates (x, y).
            seed: 随机种子，默认None表示随机 / Random seed, None means random.
        """
        current_pos = pyautogui.position()
        self.move_and_click((current_pos.x, current_pos.y), end_point, seed)
    
    def double_click_at(self, end_point: Tuple[float, float], seed: Optional[int] = None):
        """
        从当前鼠标位置移动到目标位置并双击
        Moves from current mouse position to target and double-clicks.
        
        Args:
            end_point: 目标坐标 (x, y) / Target coordinates (x, y).
            seed: 随机种子，默认None表示随机 / Random seed, None means random.
        """
        current_pos = pyautogui.position()
        self.move_and_double_click((current_pos.x, current_pos.y), end_point, seed)
    
    def right_click_at(self, end_point: Tuple[float, float], seed: Optional[int] = None):
        """
        从当前鼠标位置移动到目标位置并右击
        Moves from current mouse position to target and right-clicks.
        
        Args:
            end_point: 目标坐标 (x, y) / Target coordinates (x, y).
            seed: 随机种子，默认None表示随机 / Random seed, None means random.
        """
        current_pos = pyautogui.position()
        self.move_and_right_click((current_pos.x, current_pos.y), end_point, seed)
    
    def drag_to(self, end_point: Tuple[float, float], seed: Optional[int] = None):
        """
        从当前鼠标位置拖拽到目标位置
        Drags from current mouse position to target position.
        
        Args:
            end_point: 目标坐标 (x, y) / Target coordinates (x, y).
            seed: 随机种子，默认None表示随机 / Random seed, None means random.
        """
        current_pos = pyautogui.position()
        self.drag((current_pos.x, current_pos.y), end_point, seed)