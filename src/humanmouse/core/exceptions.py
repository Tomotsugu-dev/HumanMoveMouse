"""
异常类定义
Exception class definitions
"""


class HumanMouseError(Exception):
    """HumanMouse库的基础异常类"""
    pass


class ConfigurationError(HumanMouseError):
    """配置相关错误"""
    pass


class TrajectoryError(HumanMouseError):
    """轨迹相关错误"""
    pass


class ModelError(HumanMouseError):
    """模型相关错误"""
    pass


class StorageError(HumanMouseError):
    """存储相关错误"""
    pass


class ControllerError(HumanMouseError):
    """控制器相关错误"""
    pass


class ValidationError(HumanMouseError):
    """数据验证错误"""
    pass