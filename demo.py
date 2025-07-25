"""
demo.py - Main Control Panel for Human Mouse Simulation

This script serves as the central, interactive entry point for the entire
human mouse simulation project. It provides a text-based menu to access
various functionalities from different modules, including:
- Real-time mouse coordinate tracking.
- Demonstrations of different mouse actions (move, click, drag).
- Demonstrations of controller parameter tuning (speed, jitter).
- Training a new mouse movement model from collected CSV data.

Usage:
    Run this script from the project's root directory:
    python demo.py
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from mouse_utils.position_tracker import track_mouse_position
from demos.basic_demo_simple import run_basic_actions_demo
from demos.parameter_tuning_demo import run_parameter_demo
from demos.drag_demo import run_drag_demo
from scripts.train_model import train_and_save_model

def main_menu():
    """Displays the main menu and handles user input."""
    while True:
        print("\n" + "="*40)
        print("      Human Mouse Control Panel")
        print("="*40)
        print("1. Track Mouse Position (for 120s)")
        print("\n--- Demonstrations ---")
        print("2. Demo: Basic Actions (Move, Click, Drag)")
        print("3. Demo: Parameter Tuning (Speed, Jitter)")
        print("4. Demo: Drag")
        print("\n--- System ---")
        print("5. Train New Mouse Model")
        print("6. Exit")
        print("-"*40)
        
        choice = input("Please enter your choice (1-6): ")
        
        if choice == '1':
            print("\n--> Starting Mouse Tracker...")
            track_mouse_position(120)
            
        elif choice == '2':
            run_basic_actions_demo()
            
        elif choice == '3':
            run_parameter_demo()

        elif choice == '4':
            run_drag_demo()

        elif choice == '5':
            print("\n--> Starting model training...")
            train_and_save_model()

        elif choice == '6':
            print("Exiting...")
            break
            
        else:
            print("\n[Error] Invalid choice. Please try again.")
        
        # Pause to allow user to see results before showing menu again
        if choice in ('1', '2', '3', '4', '5'):
             input("\nPress Enter to return to the menu...")

def main():
    """Main entry point"""
    main_menu()

if __name__ == "__main__":
    main()