"""
数据存储层实现
提供轨迹数据的持久化存储功能
"""
import csv
import json
import pickle
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib

from .base import ITrajectoryStorage, Trajectory, TrajectoryPoint


class CSVTrajectoryStorage(ITrajectoryStorage):
    """CSV格式的轨迹存储实现"""
    
    def __init__(self, base_path: str = "../csv_data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, trajectory: Trajectory, filename: Optional[str] = None) -> str:
        """
        保存轨迹到CSV文件
        返回保存的文件路径
        """
        if filename is None:
            filename = self._generate_filename(trajectory)
        
        filepath = self.base_path / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # 写入头部
                writer.writerow(['x_coordinate', 'y_coordinate', 'time_interval_seconds'])
                
                # 写入轨迹点
                for i, point in enumerate(trajectory.points):
                    if i == 0:
                        time_interval = 0
                    else:
                        time_interval = point.timestamp - trajectory.points[i-1].timestamp
                    
                    writer.writerow([
                        round(point.x, 2),
                        round(point.y, 2),
                        round(time_interval, 4)
                    ])
            
            # 保存元数据
            self._save_metadata(trajectory, filepath)
            
            return str(filepath)
            
        except Exception as e:
            raise IOError(f"Failed to save trajectory: {e}")
    
    def load(self, filename: str) -> Optional[Trajectory]:
        """从CSV文件加载轨迹"""
        filepath = self.base_path / filename
        
        if not filepath.exists():
            return None
        
        try:
            points = []
            cumulative_time = 0.0
            
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    time_interval = float(row['time_interval_seconds'])
                    cumulative_time += time_interval
                    
                    point = TrajectoryPoint(
                        x=float(row['x_coordinate']),
                        y=float(row['y_coordinate']),
                        timestamp=cumulative_time
                    )
                    points.append(point)
            
            # 加载元数据
            metadata = self._load_metadata(filepath)
            
            # 构造轨迹对象
            trajectory = Trajectory(
                points=points,
                start_time=metadata.get('start_time', datetime.now()),
                end_time=metadata.get('end_time', datetime.now()),
                metadata=metadata
            )
            
            return trajectory
            
        except Exception as e:
            raise IOError(f"Failed to load trajectory: {e}")
    
    def list_trajectories(self) -> List[str]:
        """列出所有CSV轨迹文件"""
        return [f.name for f in self.base_path.glob("*.csv")]
    
    def _generate_filename(self, trajectory: Trajectory) -> str:
        """生成唯一的文件名"""
        if len(trajectory.points) < 2:
            raise ValueError("Trajectory must have at least 2 points")
        
        start = trajectory.points[0]
        end = trajectory.points[-1]
        
        # 生成哈希码
        hash_data = f"{trajectory.start_time.isoformat()}{len(trajectory.points)}{start.x}{start.y}{end.x}{end.y}"
        hash_code = hashlib.md5(hash_data.encode()).hexdigest()[:8]
        
        filename = f"X{start.x:.1f}Y{start.y:.1f}_X{end.x:.1f}Y{end.y:.1f}_{hash_code}.csv"
        return filename
    
    def _save_metadata(self, trajectory: Trajectory, filepath: Path):
        """保存轨迹元数据"""
        metadata_file = filepath.with_suffix('.meta.json')
        
        metadata = {
            'start_time': trajectory.start_time.isoformat(),
            'end_time': trajectory.end_time.isoformat(),
            'duration': trajectory.duration,
            'total_distance': trajectory.total_distance,
            'average_speed': trajectory.average_speed,
            'point_count': len(trajectory.points),
            **trajectory.metadata
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_metadata(self, filepath: Path) -> Dict[str, Any]:
        """加载轨迹元数据"""
        metadata_file = filepath.with_suffix('.meta.json')
        
        if not metadata_file.exists():
            return {}
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            # 转换时间字符串
            if 'start_time' in metadata:
                metadata['start_time'] = datetime.fromisoformat(metadata['start_time'])
            if 'end_time' in metadata:
                metadata['end_time'] = datetime.fromisoformat(metadata['end_time'])
                
            return metadata
        except Exception:
            return {}


class PickleModelStorage:
    """Pickle格式的模型存储"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_model(self, model: Any, filename: str) -> str:
        """保存模型到pickle文件"""
        filepath = self.base_path / filename
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
            return str(filepath)
        except Exception as e:
            raise IOError(f"Failed to save model: {e}")
    
    def load_model(self, filename: str) -> Any:
        """从pickle文件加载模型"""
        filepath = self.base_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            raise IOError(f"Failed to load model: {e}")