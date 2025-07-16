# HumanMoveMouse 🖱️

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

🎯 **Human-like mouse automation using statistical models and minimum-jerk interpolation.**

---

## Overview

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


