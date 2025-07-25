"""
核心基类和接口定义
提供系统的基础抽象
"""
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TrajectoryPoint:
    """轨迹点数据结构"""
    x: float
    y: float
    timestamp: float
    velocity: Optional[float] = None
    acceleration: Optional[float] = None


@dataclass
class Trajectory:
    """完整轨迹数据结构"""
    points: List[TrajectoryPoint]
    start_time: datetime
    end_time: datetime
    metadata: Dict[str, Any]
    
    @property
    def duration(self) -> float:
        """获取轨迹持续时间（秒）"""
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def total_distance(self) -> float:
        """计算轨迹总距离"""
        if len(self.points) < 2:
            return 0.0
        
        distance = 0.0
        for i in range(1, len(self.points)):
            dx = self.points[i].x - self.points[i-1].x
            dy = self.points[i].y - self.points[i-1].y
            distance += (dx**2 + dy**2)**0.5
        
        return distance
    
    @property
    def average_speed(self) -> float:
        """计算平均速度"""
        if self.duration == 0:
            return 0.0
        return self.total_distance / self.duration


class ITrajectoryCollector(ABC):
    """轨迹收集器接口"""
    
    @abstractmethod
    def start_collection(self, start_point: Tuple[float, float]) -> None:
        """开始收集轨迹"""
        pass
    
    @abstractmethod
    def collect_point(self, position: Tuple[float, float]) -> None:
        """收集一个轨迹点"""
        pass
    
    @abstractmethod
    def finish_collection(self, end_point: Tuple[float, float]) -> Trajectory:
        """结束收集并返回轨迹"""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """重置收集器状态"""
        pass


class ITrajectoryGenerator(ABC):
    """轨迹生成器接口"""
    
    @abstractmethod
    def generate(self, 
                start_point: Tuple[float, float],
                end_point: Tuple[float, float],
                **kwargs) -> Trajectory:
        """生成轨迹"""
        pass


class ITrajectoryStorage(ABC):
    """轨迹存储接口"""
    
    @abstractmethod
    def save(self, trajectory: Trajectory, filename: str) -> bool:
        """保存轨迹"""
        pass
    
    @abstractmethod
    def load(self, filename: str) -> Optional[Trajectory]:
        """加载轨迹"""
        pass
    
    @abstractmethod
    def list_trajectories(self) -> List[str]:
        """列出所有可用轨迹"""
        pass


class IMouseController(ABC):
    """鼠标控制器接口"""
    
    @abstractmethod
    def move(self, trajectory: Trajectory) -> None:
        """按照轨迹移动鼠标"""
        pass
    
    @abstractmethod
    def click(self, button: str = 'left') -> None:
        """执行鼠标点击"""
        pass
    
    @abstractmethod
    def drag(self, trajectory: Trajectory) -> None:
        """执行拖拽操作"""
        pass


class BaseComponent:
    """所有组件的基类"""
    
    def __init__(self, name: str):
        self.name = name
        self._logger = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化组件"""
        if self._initialized:
            return True
        
        try:
            self._setup()
            self._initialized = True
            return True
        except Exception as e:
            self.log_error(f"Failed to initialize {self.name}: {e}")
            return False
    
    def _setup(self):
        """子类重写此方法进行具体的初始化"""
        pass
    
    def cleanup(self):
        """清理资源"""
        pass
    
    def log_info(self, message: str):
        """记录信息日志"""
        if self._logger:
            self._logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str):
        """记录错误日志"""
        if self._logger:
            self._logger.error(f"[{self.name}] {message}")
    
    def log_debug(self, message: str):
        """记录调试日志"""
        if self._logger:
            self._logger.debug(f"[{self.name}] {message}")