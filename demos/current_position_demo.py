"""
当前位置演示 - 演示从当前鼠标位置开始的移动功能
Current Position Demo - Demonstrates movement from current mouse position
"""
import time
import sys
import os

# Add paths for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Use original imports
from human_mouse.human_mouse_controller import HumanMouseController

def run_current_position_demo():
    """演示从当前鼠标位置开始的各种操作 / Demonstrates operations starting from current position"""
    print("=== Current Position Demo ===")
    print("演示从当前鼠标位置开始的移动 / Demonstrating movements from current position")
    
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
            
        controller = HumanMouseController(model_pkl=model_path)
        
        print("\n准备开始演示，请在3秒内将鼠标移动到屏幕中央...")
        print("Demo will start in 3 seconds, please move your mouse to center of screen...")
        time.sleep(3)
        
        # Define target points
        targets = [
            (200, 200),   # Top-left
            (800, 200),   # Top-right
            (800, 600),   # Bottom-right
            (200, 600),   # Bottom-left
            (500, 400),   # Center
        ]
        
        print("\n1. move_to() - 从当前位置移动到目标 / Move from current position")
        print("   目标 / Target: (200, 200)")
        controller.move_to(targets[0])
        time.sleep(1)
        
        print("\n2. click_at() - 从当前位置移动并单击 / Move from current and click")
        print("   目标 / Target: (800, 200)")
        controller.click_at(targets[1])
        time.sleep(1)
        
        print("\n3. double_click_at() - 从当前位置移动并双击 / Move from current and double-click")
        print("   目标 / Target: (800, 600)")
        controller.double_click_at(targets[2])
        time.sleep(1)
        
        print("\n4. right_click_at() - 从当前位置移动并右击 / Move from current and right-click")
        print("   目标 / Target: (200, 600)")
        controller.right_click_at(targets[3])
        time.sleep(1)
        
        print("\n5. drag_to() - 从当前位置拖拽到目标 / Drag from current position")
        print("   目标 / Target: (500, 400)")
        controller.drag_to(targets[4])
        
        print("\n=== 演示完成 / Demo Finished ===")
        
    except Exception as e:
        print(f"[Error] in current_position_demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_current_position_demo()