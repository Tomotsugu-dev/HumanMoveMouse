import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from human_mouse.human_mouse_stat_mj import train_mouse_model

def train_and_save_model():
    """Train model and save to multiple locations for compatibility"""
    # Define paths
    csv_data_path = os.path.join(parent_dir, "csv_data")
    
    # Output paths - save to multiple locations
    output_paths = [
        # Root directory (for backward compatibility)
        os.path.join(parent_dir, "mouse_model.pkl"),
        # Package location (for PyPI distribution)
        os.path.join(parent_dir, "src", "humanmouse", "models", "data", "mouse_model.pkl")
    ]
    
    # Train model and save to root first
    print(f"Training model from CSV files in: {csv_data_path}")
    train_mouse_model(csv_data_path, output_paths[0])
    print(f"Model saved to: {output_paths[0]}")
    
    # Copy to package location
    try:
        import shutil
        os.makedirs(os.path.dirname(output_paths[1]), exist_ok=True)
        shutil.copy2(output_paths[0], output_paths[1])
        print(f"Model also copied to: {output_paths[1]}")
    except Exception as e:
        print(f"Warning: Could not copy model to package location: {e}")
    
    print("\nModel training completed successfully!")
    print("The model has been saved to the following locations:")
    for path in output_paths:
        if os.path.exists(path):
            print(f"  [OK] {path}")

if __name__ == '__main__':
    train_and_save_model()