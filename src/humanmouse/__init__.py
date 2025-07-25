"""
HumanMouse - 基于真实数据的人类风格鼠标移动自动化工具
A human-like mouse movement automation tool based on real trajectory data
"""

__version__ = "1.0.0"
__author__ = "HumanMoveMouse contributors"
__email__ = ""  # Add email if needed for PyPI
__description__ = "A human-like mouse movement automation tool based on real trajectory data"

# 导出主要接口
from .controllers.mouse_controller import HumanMouseController

__all__ = [
    "HumanMouseController",
    "__version__",
]

# 简化的使用示例
def create_controller(**kwargs):
    """
    创建鼠标控制器的便捷函数
    Convenience function to create a mouse controller
    
    Args:
        **kwargs: 传递给HumanMouseController的参数
    
    Returns:
        HumanMouseController: 配置好的鼠标控制器实例
    """
    return HumanMouseController(**kwargs)