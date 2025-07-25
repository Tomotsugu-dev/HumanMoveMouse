"""
测试轨迹数据结构
Test trajectory data structures
"""
import pytest
from datetime import datetime
from humanmouse.core.trajectory import Trajectory, TrajectoryPoint


class TestTrajectoryPoint:
    """测试TrajectoryPoint类"""
    
    def test_creation(self):
        """测试创建轨迹点"""
        point = TrajectoryPoint(x=100.0, y=200.0, timestamp=1.0)
        assert point.x == 100.0
        assert point.y == 200.0
        assert point.timestamp == 1.0
        assert point.velocity is None
        assert point.acceleration is None
    
    def test_distance_to(self):
        """测试计算距离"""
        point1 = TrajectoryPoint(x=0.0, y=0.0, timestamp=0.0)
        point2 = TrajectoryPoint(x=3.0, y=4.0, timestamp=1.0)
        assert point1.distance_to(point2) == 5.0
    
    def test_as_tuple(self):
        """测试转换为元组"""
        point = TrajectoryPoint(x=100.0, y=200.0, timestamp=1.0)
        assert point.as_tuple() == (100.0, 200.0)


class TestTrajectory:
    """测试Trajectory类"""
    
    def test_creation(self):
        """测试创建轨迹"""
        trajectory = Trajectory()
        assert len(trajectory.points) == 0
        assert trajectory.metadata == {}
    
    def test_add_point(self):
        """测试添加轨迹点"""
        trajectory = Trajectory()
        point = TrajectoryPoint(x=100.0, y=200.0, timestamp=1.0)
        trajectory.add_point(point)
        assert len(trajectory.points) == 1
        assert trajectory.points[0] == point
    
    def test_properties(self):
        """测试轨迹属性"""
        trajectory = Trajectory()
        
        # 添加几个点
        trajectory.add_point(TrajectoryPoint(x=0.0, y=0.0, timestamp=0.0))
        trajectory.add_point(TrajectoryPoint(x=3.0, y=4.0, timestamp=1.0))
        trajectory.add_point(TrajectoryPoint(x=6.0, y=8.0, timestamp=2.0))
        
        # 测试起始点和结束点
        assert trajectory.start_point.x == 0.0
        assert trajectory.end_point.x == 6.0
        
        # 测试总距离
        assert trajectory.total_distance == 10.0  # 5 + 5
    
    def test_resample(self):
        """测试重采样"""
        trajectory = Trajectory()
        
        # 添加点
        for i in range(10):
            trajectory.add_point(TrajectoryPoint(x=float(i), y=float(i), timestamp=float(i)))
        
        # 重采样到5个点
        resampled = trajectory.resample(5)
        assert len(resampled.points) == 5
        
        # 检查起始和结束点保持不变
        assert resampled.points[0].x == 0.0
        assert resampled.points[-1].x == 9.0