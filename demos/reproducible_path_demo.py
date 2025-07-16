# demos/reproducible_path_demo.py
import time
from human_mouse.human_mouse_controller import HumanMouseController

def run_seed_demo():
    """Demonstrates how to generate reproducible paths using a seed."""
    print("--- Starting Reproducible Path Demo (Seed) ---")

    controller = HumanMouseController(model_pkl="mouse_model.pkl")
    point_A = (400, 300)
    point_B = (1100, 700)
    fixed_seed = 12345 # A fixed seed for reproducibility

    print("Demonstration will start in 3 seconds...")
    time.sleep(3)

    print(f"\n1. Moving from A to B with a fixed seed: {fixed_seed}. Observe the path.")
    controller.move(point_A, point_B, seed=fixed_seed)
    time.sleep(1)

    print(f"\n2. Moving again with the SAME fixed seed: {fixed_seed}. The path will be identical.")
    controller.move(point_B, point_A, seed=fixed_seed)
    time.sleep(1)

    print("\n3. Moving now with NO seed. The path will be random and different.")
    controller.move(point_A, point_B, seed=None)

    print("\n--- Reproducible Path Demo Finished ---")

if __name__ == '__main__':
    run_seed_demo()