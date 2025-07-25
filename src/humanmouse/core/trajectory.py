"""
轨迹数据结构定义
Trajectory data structure definitions
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np


@dataclass
class TrajectoryPoint:
    """
    轨迹点数据结构
    Trajectory point data structure
    """
    x: float
    y: float
    timestamp: float
    velocity: Optional[float] = None
    acceleration: Optional[float] = None
    
    def distance_to(self, other: 'TrajectoryPoint') -> float:
        """计算到另一个点的距离"""
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def as_tuple(self) -> tuple:
        """返回坐标元组"""
        return (self.x, self.y)


@dataclass
class Trajectory:
    """
    完整轨迹数据结构
    Complete trajectory data structure
    """
    points: List[TrajectoryPoint] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.start_time and self.points:
            self.start_time = datetime.now()
        if not self.end_time and self.points:
            self.end_time = datetime.now()
    
    @property
    def duration(self) -> float:
        """获取轨迹持续时间（秒）"""
        if not self.start_time or not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def total_distance(self) -> float:
        """计算轨迹总距离"""
        if len(self.points) < 2:
            return 0.0
        
        distance = 0.0
        for i in range(1, len(self.points)):
            distance += self.points[i-1].distance_to(self.points[i])
        
        return distance
    
    @property
    def average_speed(self) -> float:
        """计算平均速度（像素/秒）"""
        if self.duration == 0:
            return 0.0
        return self.total_distance / self.duration
    
    @property
    def start_point(self) -> Optional[TrajectoryPoint]:
        """获取起始点"""
        return self.points[0] if self.points else None
    
    @property
    def end_point(self) -> Optional[TrajectoryPoint]:
        """获取结束点"""
        return self.points[-1] if self.points else None
    
    def add_point(self, point: TrajectoryPoint) -> None:
        """添加轨迹点"""
        self.points.append(point)
    
    def get_coordinates(self) -> np.ndarray:
        """获取所有坐标的numpy数组"""
        if not self.points:
            return np.array([])
        return np.array([(p.x, p.y) for p in self.points])
    
    def get_time_intervals(self) -> np.ndarray:
        """获取时间间隔数组"""
        if len(self.points) < 2:
            return np.array([])
        
        intervals = []
        for i in range(1, len(self.points)):
            interval = self.points[i].timestamp - self.points[i-1].timestamp
            intervals.append(interval)
        
        return np.array(intervals)
    
    def resample(self, num_points: int) -> 'Trajectory':
        """重采样轨迹到指定点数"""
        if len(self.points) < 2 or num_points < 2:
            return self
        
        # 使用线性插值重采样
        coords = self.get_coordinates()
        old_indices = np.linspace(0, len(coords) - 1, len(coords))
        new_indices = np.linspace(0, len(coords) - 1, num_points)
        
        new_x = np.interp(new_indices, old_indices, coords[:, 0])
        new_y = np.interp(new_indices, old_indices, coords[:, 1])
        
        # 创建新的轨迹点
        new_points = []
        time_step = self.duration / (num_points - 1)
        
        for i in range(num_points):
            point = TrajectoryPoint(
                x=new_x[i],
                y=new_y[i],
                timestamp=i * time_step
            )
            new_points.append(point)
        
        return Trajectory(
            points=new_points,
            start_time=self.start_time,
            end_time=self.end_time,
            metadata=self.metadata.copy()
        )