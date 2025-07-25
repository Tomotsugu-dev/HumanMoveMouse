"""
接口定义
Interface definitions
"""
from abc import ABC, abstractmethod
from typing import Tuple, List, Optional, Any
from .trajectory import Trajectory, TrajectoryPoint


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
    
    @abstractmethod
    def set_model(self, model: Any) -> None:
        """设置生成模型"""
        pass


class ITrajectoryStorage(ABC):
    """轨迹存储接口"""
    
    @abstractmethod
    def save(self, trajectory: Trajectory, filename: Optional[str] = None) -> str:
        """保存轨迹，返回文件路径"""
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
    
    @abstractmethod
    def set_speed(self, speed_factor: float) -> None:
        """设置移动速度"""
        pass