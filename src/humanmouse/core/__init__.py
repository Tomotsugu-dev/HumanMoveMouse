"""
核心模块 - 基础数据结构和接口定义
Core module - Basic data structures and interface definitions
"""

from .trajectory import Trajectory, TrajectoryPoint
from .interfaces import (
    ITrajectoryCollector,
    ITrajectoryGenerator,
    ITrajectoryStorage,
    IMouseController,
)
from .exceptions import (
    HumanMouseError,
    ConfigurationError,
    TrajectoryError,
    ModelError,
)

__all__ = [
    "Trajectory",
    "TrajectoryPoint",
    "ITrajectoryCollector",
    "ITrajectoryGenerator", 
    "ITrajectoryStorage",
    "IMouseController",
    "HumanMouseError",
    "ConfigurationError",
    "TrajectoryError",
    "ModelError",
]