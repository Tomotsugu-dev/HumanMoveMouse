"""
HumanMouse - 基于真实数据的人类风格鼠标移动自动化工具
A human-like mouse movement automation tool based on real trajectory data
"""
from .__version__ import __version__
from .controllers.mouse_controller import HumanMouseController

__all__ = [
    "HumanMouseController",
    "create_controller",
    "__version__",
]


def create_controller(**kwargs) -> HumanMouseController:
    """
    创建鼠标控制器的便捷函数
    Convenience function to create a mouse controller.

    Args:
        **kwargs: 传递给 HumanMouseController 的参数 / Forwarded to HumanMouseController.

    Returns:
        配置好的鼠标控制器实例 / A configured HumanMouseController instance.
    """
    return HumanMouseController(**kwargs)
