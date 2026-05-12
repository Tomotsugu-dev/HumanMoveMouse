"""
当前位置演示 - 演示从当前鼠标位置开始的移动功能
Current position demo - operations that start from the live cursor position.
"""
import time

from humanmouse import HumanMouseController


def run_current_position_demo() -> None:
    """演示从当前鼠标位置开始的各种操作 / Operations starting from current position."""
    print("=== Current Position Demo ===")

    controller = HumanMouseController()

    print("\n准备开始演示，请在3秒内将鼠标移动到屏幕中央...")
    print("Demo will start in 3 seconds, please move your mouse to center of screen...")
    time.sleep(3)

    targets = [
        (200, 200),   # Top-left
        (800, 200),   # Top-right
        (800, 600),   # Bottom-right
        (200, 600),   # Bottom-left
        (500, 400),   # Center
    ]

    print("\n1. move_to() - 从当前位置移动到目标 / Move from current position")
    controller.move_to(targets[0])
    time.sleep(1)

    print("\n2. click_at() - 从当前位置移动并单击 / Move from current and click")
    controller.click_at(targets[1])
    time.sleep(1)

    print("\n3. double_click_at() - 从当前位置移动并双击 / Move from current and double-click")
    controller.double_click_at(targets[2])
    time.sleep(1)

    print("\n4. right_click_at() - 从当前位置移动并右击 / Move from current and right-click")
    controller.right_click_at(targets[3])
    time.sleep(1)

    print("\n5. drag_to() - 从当前位置拖拽到目标 / Drag from current position")
    controller.drag_to(targets[4])

    print("\n=== 演示完成 / Demo Finished ===")


if __name__ == "__main__":
    run_current_position_demo()
