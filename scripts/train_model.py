"""
从 csv_data/ 训练鼠标模型并写入随包分发位置。
Train a mouse model from csv_data/ and write it to the bundled package location.

用法 / Usage:
    uv run python scripts/train_model.py
    # 或 / or
    python scripts/train_model.py
"""
from pathlib import Path

from humanmouse.models import train_mouse_model

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT_ROOT / "csv_data"
MODEL_PATH = PROJECT_ROOT / "src" / "humanmouse" / "models" / "data" / "mouse_model.pkl"


def train_and_save_model() -> None:
    """Train model and save to the package data directory."""
    print(f"Training model from CSV files in: {CSV_DIR}")
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    train_mouse_model(str(CSV_DIR), str(MODEL_PATH))
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save_model()
