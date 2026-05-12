"""
轨迹生成的 smoke 测试 - 不真实驱动鼠标,只校验几何属性
Smoke tests for trajectory generation - geometry only, no real mouse driving.
"""
import numpy as np
import pytest

from humanmouse import HumanMouseController
from humanmouse.models import generate_mouse_trajectory, get_default_model_path


@pytest.fixture(scope="module")
def model_path() -> str:
    return get_default_model_path()


def test_trajectory_shape(model_path: str) -> None:
    """生成轨迹的形状应与 num_points 一致 / Output shape must match num_points."""
    xy, dt = generate_mouse_trajectory(
        model_path=model_path,
        start_point=(100, 100),
        end_point=(800, 600),
        num_points=50,
        jitter_amplitude=0.3,
        seed=42,
    )
    assert xy.shape == (50, 2)
    assert dt.shape == (50,)


def test_trajectory_dt_first_is_zero(model_path: str) -> None:
    """dt[0] 必须为 0,且其余为正 / dt[0] must be 0 and the rest positive."""
    _, dt = generate_mouse_trajectory(
        model_path=model_path,
        start_point=(100, 100),
        end_point=(800, 600),
        num_points=50,
        jitter_amplitude=0.3,
        seed=42,
    )
    assert dt[0] == 0.0
    assert np.all(dt[1:] >= 0.0)


def test_trajectory_endpoints_close(model_path: str) -> None:
    """起点和终点应贴近输入(jitter 会有偏移) / Endpoints should be close to inputs."""
    start = (100.0, 100.0)
    end = (800.0, 600.0)
    xy, _ = generate_mouse_trajectory(
        model_path=model_path,
        start_point=start,
        end_point=end,
        num_points=120,
        jitter_amplitude=0.0,  # 无抖动时端点应严格匹配 / strict match without jitter
        seed=42,
    )
    assert np.allclose(xy[0], start, atol=1e-3)
    assert np.allclose(xy[-1], end, atol=1e-3)


def test_trajectory_reproducible(model_path: str) -> None:
    """同 seed 应生成相同轨迹 / Same seed must yield identical trajectories."""
    kwargs = dict(
        model_path=model_path,
        start_point=(100, 100),
        end_point=(800, 600),
        num_points=80,
        jitter_amplitude=0.5,
        seed=12345,
    )
    xy1, dt1 = generate_mouse_trajectory(**kwargs)
    xy2, dt2 = generate_mouse_trajectory(**kwargs)
    np.testing.assert_array_equal(xy1, xy2)
    np.testing.assert_array_equal(dt1, dt2)


def test_straight_mode_exact_endpoints() -> None:
    """直线模式端点必须严格命中 / Straight mode must hit endpoints exactly."""
    controller = HumanMouseController(straight=True, num_points=60)
    xy, dt = controller._generate_trajectory((100.0, 100.0), (800.0, 600.0))
    assert xy.shape == (60, 2)
    np.testing.assert_array_equal(xy[0], np.float32((100.0, 100.0)))
    np.testing.assert_array_equal(xy[-1], np.float32((800.0, 600.0)))
    assert dt[0] == 0.0


def test_straight_mode_zero_perpendicular_offset() -> None:
    """直线模式所有点应位于起终连线上 / All points must lie on the start-end line."""
    start = np.array([100.0, 100.0], dtype=np.float32)
    end = np.array([800.0, 600.0], dtype=np.float32)
    controller = HumanMouseController(straight=True, num_points=80)
    xy, _ = controller._generate_trajectory(tuple(start), tuple(end))

    direction = end - start
    direction /= np.linalg.norm(direction)
    perp = np.array([-direction[1], direction[0]], dtype=np.float32)
    offsets = (xy - start) @ perp
    assert np.max(np.abs(offsets)) < 1e-3
