"""
项目交互式控制台
Interactive control panel for the human mouse simulation project.

用法 / Usage:
    uv run python demo.py
"""
from demos.basic_actions_demo import run_basic_actions_demo
from demos.current_position_demo import run_current_position_demo
from demos.drag_demo import run_drag_demo
from demos.parameter_tuning_demo import run_parameter_demo
from demos.reproducible_path_demo import run_seed_demo
from humanmouse.utils import track_mouse_position
from scripts.train_model import train_and_save_model


MENU = """
========================================
      Human Mouse Control Panel
========================================
1. Track Mouse Position (for 120s)

--- Demonstrations ---
2. Demo: Basic Actions (Move, Click, Drag)
3. Demo: Parameter Tuning (Speed, Jitter)
4. Demo: Drag
5. Demo: Current Position API
6. Demo: Reproducible Path (Seed)

--- System ---
7. Train New Mouse Model
8. Exit
----------------------------------------
"""

ACTIONS = {
    "1": ("Starting mouse tracker...", lambda: track_mouse_position(120)),
    "2": (None, run_basic_actions_demo),
    "3": (None, run_parameter_demo),
    "4": (None, run_drag_demo),
    "5": (None, run_current_position_demo),
    "6": (None, run_seed_demo),
    "7": ("Starting model training...", train_and_save_model),
}


def main_menu() -> None:
    """Display the main menu and dispatch to handlers."""
    while True:
        print(MENU)
        choice = input("Please enter your choice (1-8): ").strip()

        if choice == "8":
            print("Exiting...")
            return

        action = ACTIONS.get(choice)
        if action is None:
            print("\n[Error] Invalid choice. Please try again.")
            continue

        banner, handler = action
        if banner:
            print(f"\n--> {banner}")
        handler()
        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    main_menu()
