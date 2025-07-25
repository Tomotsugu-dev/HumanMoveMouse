import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from human_mouse.human_mouse_controller import HumanMouseController

def run_drag_demo(start = (1747, 721),
                  end = (1943, 721)
                  ):
    """
    Runs a pre-defined mouse drag demonstration.
    This function is designed to be called from a main script in the root directory.
    """
    try:
        # Try to find model in multiple locations
        model_paths = [
            os.path.join(parent_dir, "mouse_model.pkl"),
            os.path.join(parent_dir, "src", "humanmouse", "models", "data", "mouse_model.pkl"),
            "mouse_model.pkl"
        ]
        
        model_path = None
        for path in model_paths:
            if os.path.exists(path):
                model_path = path
                break
        
        if not model_path:
            print("Error: Cannot find mouse_model.pkl")
            return
            
        # Create a controller instance.
        controller = HumanMouseController(
            model_pkl=model_path,
            num_points=100,
            jitter_amplitude=0.5
        )

        # Define start and end points.


        print("--> Running drag and drop demo...")
        print(f"    From: {start} -> To: {end}")
        controller.drag(start, end)
        print("--> Drag demo finished!")

    except FileNotFoundError:
        print("\n[Error] 'mouse_model.pkl' not found.")
        print("Please run the training script first.")
    except Exception as e:
        print(f"\n[Error] An unexpected error occurred in the drag demo: {e}")

# This part allows the script to be run standalone for testing purposes
if __name__ == '__main__':
    print("Running drag_demo.py as a standalone script for testing...")
    run_drag_demo()