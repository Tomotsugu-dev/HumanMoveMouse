"""
可复现轨迹演示
Reproducible path demo - same seed yields the same trajectory.
"""
import time

from humanmouse import HumanMouseController


def run_seed_demo() -> None:
    """Demonstrates reproducible paths using a fixed seed."""
    print("--- Starting Reproducible Path Demo (Seed) ---")

    controller = HumanMouseController()
    point_a = (400, 300)
    point_b = (1100, 700)
    fixed_seed = 12345

    print("Demonstration will start in 3 seconds...")
    time.sleep(3)

    print(f"\n1. Moving from A to B with a fixed seed: {fixed_seed}. Observe the path.")
    controller.move(point_a, point_b, seed=fixed_seed)
    time.sleep(1)

    print(f"\n2. Moving again with the SAME fixed seed: {fixed_seed}. The path will be identical.")
    controller.move(point_b, point_a, seed=fixed_seed)
    time.sleep(1)

    print("\n3. Moving now with NO seed. The path will be random and different.")
    controller.move(point_a, point_b, seed=None)

    print("\n--- Reproducible Path Demo Finished ---")


if __name__ == "__main__":
    run_seed_demo()
