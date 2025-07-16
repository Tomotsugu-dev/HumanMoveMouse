# demos/basic_actions_demo.py
import time
from human_mouse.human_mouse_controller import HumanMouseController

def run_basic_actions_demo(        
        point_A = (200, 200),
        point_B = (800, 200),
        point_C = (800, 600),
        point_D = (200, 600)):
    """Demonstrates all basic mouse actions in a sequence with visual indicators."""
    print("--- Starting Basic Actions Demo ---")
    
    try:
        controller = HumanMouseController(model_pkl="mouse_model.pkl")
        
        print("Demonstration will start in 3 seconds... Please do not move the mouse.")
        time.sleep(3)

        # 1. Move Only
        print("1. Demonstrating: Move Only (from A to B)")
        controller.move(point_A, point_B)
        time.sleep(1)

        # 2. Move and Click
        print("2. Demonstrating: Move and Click (from B to C)")
        controller.move_and_click(point_B, point_C)
        time.sleep(1)

        # 3. Move and Double-Click
        print("3. Demonstrating: Move and Double-Click (from C to D)")
        controller.move_and_double_click(point_C, point_D)
        time.sleep(1)

        # 4. Move and Right-Click
        print("4. Demonstrating: Move and Right-Click (at current location D)")
        controller.move_and_right_click(point_D, point_D)
        time.sleep(1)

        # 5. Drag and Drop
        print("5. Demonstrating: Drag and Drop (from D back to A)")
        controller.drag(point_D, point_A)

        print("\n--- Basic Actions Demo Finished ---")

    except Exception as e:
        print(f"[Error] in basic_actions_demo: {e}")

if __name__ == '__main__':
    run_basic_actions_demo()