"""
拖拽演示
Drag demo - press, drag along a human-like trajectory, release.
"""
from humanmouse import HumanMouseController


def run_drag_demo(
    start: tuple[int, int] = (1747, 721),
    end: tuple[int, int] = (1943, 721),
) -> None:
    """Run a pre-defined mouse drag demonstration."""
    controller = HumanMouseController(num_points=100, jitter_amplitude=0.5)

    print("--> Running drag and drop demo...")
    print(f"    From: {start} -> To: {end}")
    controller.drag(start, end)
    print("--> Drag demo finished!")


if __name__ == "__main__":
    run_drag_demo()
