"""
Human Mouse Package
A package for simulating human-like mouse movements
"""
import os

# Get the package directory
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory
PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)

# Default model path - look in multiple locations
DEFAULT_MODEL_PATHS = [
    os.path.join(PROJECT_ROOT, "mouse_model.pkl"),
    os.path.join(PROJECT_ROOT, "src", "humanmouse", "models", "data", "mouse_model.pkl"),
    os.path.join(PACKAGE_DIR, "mouse_model.pkl"),
]

def get_default_model_path():
    """Get the default model path by searching in standard locations"""
    for path in DEFAULT_MODEL_PATHS:
        if os.path.exists(path):
            return path
    # If not found, return the first path (will raise error later)
    return DEFAULT_MODEL_PATHS[0]

from .human_mouse_controller import HumanMouseController

__all__ = ['HumanMouseController', 'get_default_model_path']