"""
版本信息管理
Version information management
"""

__version__ = "1.0.0"
__version_info__ = tuple(int(x) for x in __version__.split("."))

# 版本历史
VERSION_HISTORY = {
    "1.0.0": {
        "date": "2025-01-01",
        "changes": [
            "Initial release",
            "Human-like mouse trajectory generation",
            "Multiple mouse actions support",
            "Customizable parameters",
            "Model training capability",
        ]
    }
}