"""
自定义异常类
提供系统特定的异常类型
"""


class MouseTrajectoryError(Exception):
    """鼠标轨迹系统的基础异常类"""
    pass


class ConfigurationError(MouseTrajectoryError):
    """配置相关错误"""
    pass


class TrajectoryCollectionError(MouseTrajectoryError):
    """轨迹收集相关错误"""
    pass


class TrajectoryGenerationError(MouseTrajectoryError):
    """轨迹生成相关错误"""
    pass


class ModelError(MouseTrajectoryError):
    """模型相关错误"""
    pass


class StorageError(MouseTrajectoryError):
    """存储相关错误"""
    pass


class ValidationError(MouseTrajectoryError):
    """数据验证错误"""
    pass


class ControllerError(MouseTrajectoryError):
    """控制器相关错误"""
    pass