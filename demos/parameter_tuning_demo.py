"""
参数调试演示
Parameter tuning demo - speed_factor / jitter_amplitude / num_points.
"""
import time

from humanmouse import HumanMouseController


def run_parameter_demo() -> None:
    """Demonstrates the effect of different controller parameters."""
    print("--- Starting Parameter Tuning Demo ---")

    point_a = (300, 500)
    point_b = (1000, 500)

    print("Demonstration will start in 3 seconds... Please observe the mouse path carefully.")
    time.sleep(3)

    # --- Part 1: Speed Factor ---
    print("\n1. Demonstrating 'speed_factor'.")
    controller = HumanMouseController()

    print("  - Speed: 0.5x (Slow)")
    controller.set_speed(0.5)
    controller.move(point_a, point_b)
    time.sleep(0.5)

    print("  - Speed: 1.0x (Normal)")
    controller.set_speed(1.0)
    controller.move(point_b, point_a)
    time.sleep(0.5)

    print("  - Speed: 3.0x (Fast)")
    controller.set_speed(3.0)
    controller.move(point_a, point_b)
    time.sleep(1)

    # --- Part 2: Jitter Amplitude ---
    print("\n2. Demonstrating 'jitter_amplitude'.")
    print("  - Jitter: 0.2 (Very smooth path)")
    HumanMouseController(jitter_amplitude=0.2).move(point_b, point_a)
    time.sleep(0.5)

    print("  - Jitter: 5.0 (Very shaky path)")
    HumanMouseController(jitter_amplitude=5.0).move(point_a, point_b)
    time.sleep(1)

    # --- Part 3: Number of Points ---
    print("\n3. Demonstrating 'num_points'.")
    print("  - Num Points: 20 (Faster, less smooth)")
    HumanMouseController(num_points=20).move(point_b, point_a)
    time.sleep(0.5)

    print("  - Num Points: 200 (Slower, very smooth)")
    HumanMouseController(num_points=200).move(point_a, point_b)

    print("\n--- Parameter Tuning Demo Finished ---")


if __name__ == "__main__":
    run_parameter_demo()
