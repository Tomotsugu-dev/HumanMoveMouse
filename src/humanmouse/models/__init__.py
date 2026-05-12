"""
模型模块 - 轨迹生成和预测模型
Models module - Trajectory generation and prediction models
"""
from pathlib import Path

from .trajectory_model import (
    HumanMouseModel,
    generate_mouse_trajectory,
    train_mouse_model,
)

# 默认模型路径(随包分发) / Default model path bundled with the package
_DEFAULT_MODEL_PATH = Path(__file__).parent / "data" / "mouse_model.pkl"


def get_default_model_path() -> str:
    """
    获取默认模型文件路径。
    Get the bundled default model file path.

    Raises:
        FileNotFoundError: 找不到默认模型时抛出 / When the bundled model is missing.
    """
    if _DEFAULT_MODEL_PATH.exists():
        return str(_DEFAULT_MODEL_PATH)
    raise FileNotFoundError(
        f"Default model not found at {_DEFAULT_MODEL_PATH}. "
        "Run `python -m humanmouse.scripts.train_model` to generate it."
    )


__all__ = [
    "HumanMouseModel",
    "generate_mouse_trajectory",
    "train_mouse_model",
    "get_default_model_path",
]
