#!/usr/bin/env python3
"""
Human_Mouse_Controller.py
使用 human_mouse_stat_mj 模型生成仿真鼠标轨迹并执行各种鼠标操作
Generates simulated mouse trajectories using the human_mouse_stat_mj model and performs various mouse operations.
"""

import time
import random
from typing import Tuple, Optional
import numpy as np
import pyautogui

# 导入轨迹生成函数 / Import the trajectory generation function
from .human_mouse_stat_mj import generate_mouse_trajectory

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

    def __init__(self,
                 model_pkl: str,
                 num_points: int = 100,
                 jitter_amplitude: float = 0.3,
                 speed_factor: float = 1.0):
        """
        初始化鼠标控制器
        Initializes the mouse controller.

        Args:
            model_pkl: 训练好的模型文件路径（必须）/ Path to the trained model file (required).
            num_points: 轨迹采样点数，默认100 / Number of points for trajectory sampling, default is 100.
            jitter_amplitude: 抖动幅度，默认0.3 / Amplitude of the jitter, default is 0.3.
            speed_factor: 速度因子，默认1.0，值越大移动越快 / Speed factor, default is 1.0, higher values mean faster movement.
        """
        self.model_pkl = model_pkl
        self.num_points = num_points
        self.jitter_amplitude = jitter_amplitude
        self.speed_factor = speed_factor

        # 配置 pyautogui / Configure pyautogui
        pyautogui.MINIMUM_DURATION = 0.0  # 最小移动时间 / Minimum duration for a move
        pyautogui.MINIMUM_SLEEP = 0.0     # 最小睡眠时间 / Minimum sleep time
        pyautogui.PAUSE = 0.0             # 命令间暂停时间 / Pause between commands

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
            seed: 随机种子，默认None表示随机 / Random seed, None means random.

        Returns:
            xy: 轨迹坐标数组 (N, 2) / Trajectory coordinate array (N, 2).
            dt: 时间间隔数组 (N,) / Time interval array (N,).
        """
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
            if dt[i] > 0:
                adjusted_delay = dt[i] / self.speed_factor
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
                adjusted_delay = dt[i] / self.speed_factor
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


# 使用示例 / Example Usage
if __name__ == "__main__":
    # 创建控制器实例 / Create a controller instance.
    # NOTE: You must have the "mouse_model.pkl" file in the same directory.
    controller = HumanMouseController(
        model_pkl="mouse_model.pkl",
        num_points=100,
        jitter_amplitude=0.5,
        speed_factor=1.0  # 正常速度 / Normal speed
    )

    # 定义起始和结束点 / Define start and end points.
    start = (100, 100)
    end = (800, 600)

    print("Demonstration will start in 5 seconds...")
    time.sleep(5)

    # 演示不同速度 / Demonstrate different speeds
    print("===== Normal Speed (1x) =====")
    print("1. Move Only")
    controller.move(start, end)
    time.sleep(1)

    print("\n===== Fast Speed (2x) =====")
    controller.set_speed(2.0)  # 2倍速 / 2x speed
    print("2. Move and Click (2x speed)")
    controller.move_and_click(end, (500, 400))
    time.sleep(1)

    print("\n===== Super Fast Speed (5x) =====")
    controller.set_speed(5.0)  # 5倍速 / 5x speed
    print("3. Move and Double-Click (5x speed)")
    controller.move_and_double_click((500, 400), (300, 300))
    time.sleep(1)

    print("\n===== Slow Speed (0.5x) =====")
    controller.set_speed(0.5)  # 0.5倍速（慢速）/ 0.5x speed (slow)
    print("4. Move and Right-Click (0.5x speed)")
    controller.move_and_right_click((300, 300), (600, 500))
    time.sleep(1)

    print("\n===== Back to Normal Speed (1x) =====")
    controller.set_speed(1.0)  # 恢复正常速度 / Back to normal speed
    print("5. Drag and Move (1x speed)")
    controller.drag((600, 500), start)

    print("\nDemonstration finished!")