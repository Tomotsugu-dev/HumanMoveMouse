"""
配置管理模块
管理系统所有配置参数，支持环境变量覆盖
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class DisplayConfig:
    """显示相关配置"""
    window_width: int = 1200
    window_height: int = 800
    fps: int = 60
    
    # 颜色定义
    color_black: tuple = (0, 0, 0)
    color_white: tuple = (255, 255, 255)
    color_green: tuple = (0, 255, 0)
    color_red: tuple = (255, 0, 0)
    color_blue: tuple = (0, 0, 255)
    color_gray: tuple = (128, 128, 128)


@dataclass
class TrajectoryConfig:
    """轨迹采集配置"""
    point_radius: int = 15
    min_distance: int = 200  # 起止点最小距离
    csv_output_dir: str = "../csv_data"
    
    # 轨迹记录参数
    sample_rate: int = 60  # Hz
    max_trajectory_points: int = 10000


@dataclass
class ModelConfig:
    """模型相关配置"""
    default_model_path: str = "mouse_model.pkl"
    num_points: int = 100
    jitter_amplitude: float = 0.3
    speed_factor: float = 1.0
    
    # 训练参数
    min_training_samples: int = 100
    feature_extraction_params: dict = None
    
    def __post_init__(self):
        if self.feature_extraction_params is None:
            self.feature_extraction_params = {
                'velocity_bins': 20,
                'acceleration_bins': 15,
                'angle_bins': 36
            }


@dataclass
class SystemConfig:
    """系统级配置"""
    debug_mode: bool = False
    log_level: str = "INFO"
    log_file: Optional[str] = "mouse_trajectory.log"
    
    # 性能配置
    enable_caching: bool = True
    cache_size_mb: int = 100
    
    # 安全配置
    max_file_size_mb: int = 50
    allowed_file_extensions: tuple = ('.csv', '.pkl')


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.display = DisplayConfig()
        self.trajectory = TrajectoryConfig()
        self.model = ModelConfig()
        self.system = SystemConfig()
        
        # 从环境变量加载配置
        self._load_from_env()
        
        # 从配置文件加载（如果提供）
        if config_file:
            self._load_from_file(config_file)
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # 示例：MOUSE_TRACKER_DEBUG=true
        if os.getenv('MOUSE_TRACKER_DEBUG', '').lower() == 'true':
            self.system.debug_mode = True
        
        if os.getenv('MOUSE_TRACKER_LOG_LEVEL'):
            self.system.log_level = os.getenv('MOUSE_TRACKER_LOG_LEVEL')
    
    def _load_from_file(self, config_file: str):
        """从配置文件加载配置"""
        # 这里可以实现JSON/YAML配置文件的加载
        pass
    
    def get_csv_output_path(self) -> Path:
        """获取CSV输出目录路径"""
        path = Path(self.trajectory.csv_output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def validate(self) -> bool:
        """验证配置的有效性"""
        # 检查必要的目录是否存在或可创建
        try:
            self.get_csv_output_path()
        except Exception:
            return False
        
        # 验证数值范围
        if self.trajectory.point_radius <= 0:
            return False
        
        if self.model.num_points <= 0:
            return False
        
        return True


# 全局配置实例
config = ConfigManager()