"""
基础动作演示
Basic actions demo - move / click / double-click / right-click / drag.
"""
import time

from humanmouse import HumanMouseController


def run_basic_actions_demo(
    point_a: tuple[int, int] = (200, 200),
    point_b: tuple[int, int] = (800, 200),
    point_c: tuple[int, int] = (800, 600),
    point_d: tuple[int, int] = (200, 600),
) -> None:
    """Demonstrates all basic mouse actions in a sequence."""
    print("--- Starting Basic Actions Demo ---")
    controller = HumanMouseController()

    print("Demonstration will start in 3 seconds... Please do not move the mouse.")
    time.sleep(3)

    print("1. Move Only (A -> B)")
    controller.move(point_a, point_b)
    time.sleep(1)

    print("2. Move and Click (B -> C)")
    controller.move_and_click(point_b, point_c)
    time.sleep(1)

    print("3. Move and Double-Click (C -> D)")
    controller.move_and_double_click(point_c, point_d)
    time.sleep(1)

    print("4. Move and Right-Click (at D)")
    controller.move_and_right_click(point_d, point_d)
    time.sleep(1)

    print("5. Drag and Drop (D -> A)")
    controller.drag(point_d, point_a)

    print("--- Basic Actions Demo Finished ---")


if __name__ == "__main__":
    run_basic_actions_demo()
