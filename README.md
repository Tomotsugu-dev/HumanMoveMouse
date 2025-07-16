# HumanMoveMouse 🖱️

![PyPI](https://img.shields.io/pypi/v/HumanMoveMouse)[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

🎯 **Human-like mouse automation using statistical models and minimum-jerk interpolation.**

---

## Overview

**HumanMoveMouse** is a human-like mouse automation tool built on over **300 real human mouse movement samples**.

By extracting key statistical features from these trajectories and combining them with minimum-jerk interpolation, the tool enables the generation of natural, smooth, and realistic cursor paths.

These paths closely mimic real human behavior and are ideal for automation tasks requiring authenticity, such as UI testing, game botting, or user behavior simulation.

---

## Features

- **Human-like Trajectory Generation**: Generates mouse paths that follow human-like patterns based on a real-data model.

- **Multiple Mouse Actions**: Supports various common operations, including moving, clicking, double-clicking, right-clicking, and dragging.

- **Highly Customizable**:
  
  - **Speed Control**: Adjust movement speed via the `speed_factor` parameter.
  
  - **Trajectory Smoothness**: Control the number of points in the trajectory with the `num_points` parameter.
  
  - **Jitter Effect**: Add random jitter to make movements more realistic with the `jitter_amplitude` parameter.

- **Reproducibility**: By setting a random seed (`seed`), you can generate the exact same mouse trajectory, which is useful for debugging and testing.

- **Trainable Model**: Users can train a model on their own mouse trajectory data to better suit specific use cases.

---

## Installation

You can install the package directly from PyPI:

```bash
pip install HumanMoveMouse
```

Alternatively, you can install the required dependencies manually:

```bash
pip install numpy pandas scipy scikit-learn pyautogui
```

If you need to use the data collection feature to train your own model, please install `pygame` as well:

```bash
pip install pygame
```

---

## Core Functions & Code Examples

### 1. Initialize the Controller

Before using any functions, you first need to create an instance of `HumanMouseController`. The library includes a default pre-trained model (`mouse_model.pkl`) that is loaded automatically upon initialization.

```python
from humanmouse import HumanMouseController
# Create a controller instance
# This will use the library's built-in default model
controller = HumanMouseController()
```

**Notes:**

- **Custom Parameters**:
  
  - `model_pkl`: Path to a custom-trained statistical model.
  
  - `num_points`: The number of sample points in the trajectory. A higher value results in a smoother path. Default is `100`.
  
  - `jitter_amplitude`: The magnitude of random jitter added to the trajectory. `0` means no jitter. Default is `0.3`.
  
  - `speed_factor`: Controls the mouse movement speed. Values greater than `1.0` speed it up, while values less than `1.0` slow it down. Default is `1.0`.

### 2. Basic Movement

Move the cursor smoothly from one point to another.

```python
# Define start and end points
start_point = (100, 100)
end_point = (800, 600)

# Execute the move operation
controller.move(start_point, end_point)
```

**Notes:**

- `move(start_point, end_point, seed=None)`:
  
  - `start_point`: A tuple `(x, y)` representing the starting coordinates for the mouse movement.
  
  - `end_point`: A tuple `(x, y)` representing the target coordinates for the mouse movement.
  
  - `seed` (optional): An integer used to reproduce the exact same trajectory.

### 3. Move and Click

Move to a specified location and then perform a single click.

```python
start_point = (800, 600)
end_point = (400, 400)

# Execute the move and click operation
controller.move_and_click(start_point, end_point)
```

**Notes:**

- `move_and_click(start_point, end_point, seed=None)`: Takes the same arguments as the `move` method. It will simulate a short, random delay after reaching the `end_point` before performing the click.

### 4. Other Mouse Actions

Double-clicking, right-clicking, and dragging are also supported.

```python
# Move and double-click
controller.move_and_double_click((400, 400), (300, 300))

# Move and right-click
controller.move_and_right_click((300, 300), (600, 500))

# Drag and drop (press and hold left button from one point to another)
controller.drag((600, 500), (100, 100))
```

### 5. Speed Adjustment

You can dynamically adjust the mouse movement speed at any time.

```python
# Set the speed to double the original
controller.set_speed(2.0)
controller.move((100, 100), (800, 600))

# Slow down the speed to half of the original
controller.set_speed(0.5)
controller.move((800, 600), (100, 100))

# Restore to normal speed
controller.set_speed(1.0)
```

**Notes:**

- `set_speed(speed_factor)`:
  
  - `speed_factor`: The new speed factor, which must be greater than 0.

---

## Training Your Own Model

If you want the generated trajectories to better match your personal mouse usage habits, you can collect your own data and train a new model.

#### 1. Collect Data

Run the `Mouse Trajectory Collecter.py` script located in the `csv_data_collecter` directory. It will open a Pygame window. Simply move your mouse from the top-left corner to the bottom-right corner multiple times. Each movement will be saved as a CSV file in the `csv_data` directory.

```bash
python csv_data_collecter/"Mouse Trajectory Collecter.py"
```

#### 2. Train the Model

After collecting enough data (at least 100 samples are recommended), use the `train_mouse_model` function from `human_mouse_stat_mj.py` to train the model.

```python
from human_mouse import train_mouse_model 

# Specify the directory containing the CSV files and the path to save the new model
train_mouse_model("./csv_data", "my_mouse_model.pkl")

print("Model training complete!")
```

```

```

Now you can load your custom model in the controller:

controller = HumanMouseController(model_pkl="my_mouse_model.pkl")Overview

**HumanMoveMouse** is a human-like mouse automation tool built on over **300 real human mouse movement samples**.  
By extracting key statistical features from these trajectories and combining them with minimum-jerk interpolation,  
the tool enables the generation of natural, smooth, and realistic cursor paths.

These paths closely mimic real human behavior and are ideal for automation tasks requiring authenticity,  
such as UI testing, game botting, or user behavior simulation.

---

## Installation

Install the required packages using pip:

```bash
pip install numpy pandas scipy scikit-learn pyautogui pygame
```

---

## Core Functions & Examples

### Basic Movement

Move the cursor smoothly between two points.

```python
from human_mouse.human_mouse_controller import HumanMouseController 
controller = HumanMouseController(model_pkl="mouse_model.pkl") 
controller.move((100, 100), (800, 600)) # Move to coordinates 
controller.move_and_click((800, 600), (400, 400)) # Move and click
```

---

### Parameter Tuning

Adjust trajectory smoothness and speed.

```python
controller = HumanMouseController( 
    model_pkl="mouse_model.pkl", 
    num_points=200, 
    jitter_amplitude=0.2, 
    speed_factor=0.5, ) 

controller.move((300, 300), (900, 500))
```

---

### Drag and Drop

```python
controller.drag((500, 500), (700, 700))`
```

---

## Training a Model

You can train your own model using real mouse data.  
First, collect trajectory CSVs using:

```arduino
csv_data_collecter/Mouse Trajectory Collecter.py
```

Then train a model with:

```python
from human_mouse.human_mouse_stat_mj import train_mouse_model 
train_mouse_model("./csv_data", "mouse_model.pkl")`
```

---

## Demonstration

https://github.com/user-attachments/assets/3aff8057-9f25-4e83-94de-063e0c1714fd
