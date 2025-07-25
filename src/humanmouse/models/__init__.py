"""
模型模块 - 轨迹生成和预测模型
Models module - Trajectory generation and prediction models
"""

import os
from pathlib import Path

# 获取默认模型路径
DEFAULT_MODEL_PATH = Path(__file__).parent / "data" / "mouse_model.pkl"

def get_default_model_path():
    """
    获取默认模型文件路径
    Get the default model file path
    """
    if DEFAULT_MODEL_PATH.exists():
        return str(DEFAULT_MODEL_PATH)
    
    # 如果包内没有找到，尝试从当前目录查找
    local_model = Path("mouse_model.pkl")
    if local_model.exists():
        return str(local_model)
    
    raise FileNotFoundError(
        "Default model file 'mouse_model.pkl' not found. "
        "Please ensure the model file is in the package or current directory."
    )

# 导出轨迹模型相关功能
from .trajectory_model import (
    generate_mouse_trajectory,
)

__all__ = [
    "generate_mouse_trajectory", 
    "get_default_model_path"
]