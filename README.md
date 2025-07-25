# HumanMoveMouse 🖱️

![PyPI](https://img.shields.io/pypi/v/humanmovemouse)[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

🎯 **Human-like mouse automation using statistical models and minimum-jerk interpolation.**

---

## 📑 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
  - [Basic Usage](#basic-usage)
  - [Using Current Mouse Position](#using-current-mouse-position)
  - [Customizing Movement Parameters](#customizing-movement-parameters)
- [📖 API Reference](#-api-reference)
  - [HumanMouseController](#humanmousecontroller)
  - [Methods Starting from Current Position](#methods-starting-from-current-position)
- [🔧 Advanced Usage](#-advanced-usage)
  - [Using Custom Models](#using-custom-models)
  - [Training Your Own Model](#training-your-own-model)
- [📄 License](#-license)
- [⚠️ Disclaimer](#️-disclaimer)
- [🤝 Contributing](#-contributing)

---

## 🎯 Overview

**HumanMoveMouse** is a human-like mouse automation tool built on over **300 real human mouse movement samples**.

By extracting key statistical features from these trajectories and combining them with minimum-jerk interpolation, the tool enables the generation of natural, smooth, and realistic cursor paths.

These paths closely mimic real human behavior and are ideal for automation tasks requiring authenticity, such as UI testing, game botting, or user behavior simulation.

---

## ✨ Features

- **Human-like Trajectory Generation**: Generates mouse paths that follow human-like patterns based on a real-data model.

- **Multiple Mouse Actions**: Supports various common operations, including moving, clicking, double-clicking, right-clicking, and dragging.

- **Highly Customizable**:
  
  - **Speed Control**: Adjust movement speed via the `speed_factor` parameter.
  
  - **Trajectory Smoothness**: Control the number of points in the trajectory with the `num_points` parameter.
  
  - **Jitter Effect**: Add random jitter to make movements more realistic with the `jitter_amplitude` parameter.

- **Reproducibility**: By setting a random seed (`seed`), you can generate the exact same mouse trajectory, which is useful for debugging and testing.

- **Pre-trained Model**: Includes a model trained on real human mouse movements for immediate use.

---

## 📦 Installation

You can install the package directly from PyPI:

```bash
pip install HumanMoveMouse
```

---

## 🚀 Quick Start

### Basic Usage

```python
from humanmouse import HumanMouseController

# Create a controller instance
controller = HumanMouseController()

# Move the mouse
controller.move((100, 100), (800, 600))

# Move and click
controller.move_and_click((100, 100), (400, 400))

# Move and double-click
controller.move_and_double_click((400, 400), (600, 300))

# Drag and drop
controller.drag((300, 300), (500, 500))
```

### Using Current Mouse Position

```python
# New methods that start from current mouse position
controller.move_to((800, 600))              # Move from current position
controller.click_at((400, 400))             # Move and click
controller.double_click_at((600, 300))      # Move and double-click
controller.right_click_at((500, 500))       # Move and right-click
controller.drag_to((300, 300))              # Drag from current position
```

### Customizing Movement Parameters

```python
# Create controller with custom parameters
controller = HumanMouseController(
    num_points=200,           # More points = smoother movement
    jitter_amplitude=0.2,     # Less jitter = straighter path
    speed_factor=0.5          # Slower movement
)

# Set speed dynamically
controller.set_speed(2.0)  # Double speed
controller.move((100, 100), (800, 600))
```

---

## 📖 API Reference

### HumanMouseController

#### `__init__(self, model_pkl=None, num_points=100, jitter_amplitude=0.3, speed_factor=1.0)`

Initialize the controller.

**Parameters:**
- `model_pkl` (str, optional): Path to a custom model file. If None, uses the built-in model.
- `num_points` (int): Number of trajectory points. Higher = smoother. Default: 100.
- `jitter_amplitude` (float): Random jitter magnitude. 0 = no jitter. Default: 0.3.
- `speed_factor` (float): Movement speed multiplier. >1 = faster, <1 = slower. Default: 1.0.

#### `move(self, start_point, end_point, seed=None)`

Move the mouse from start to end point.

**Parameters:**
- `start_point` (tuple): Starting coordinates (x, y).
- `end_point` (tuple): Target coordinates (x, y).
- `seed` (int, optional): Random seed for reproducible trajectories.

#### `move_and_click(self, start_point, end_point, seed=None)`

Move to a location and perform a single click.

#### `move_and_double_click(self, start_point, end_point, seed=None)`

Move to a location and perform a double click.

#### `move_and_right_click(self, start_point, end_point, seed=None)`

Move to a location and perform a right click.

#### `drag(self, start_point, end_point, seed=None)`

Drag from start to end point (press and hold left button).

#### `set_speed(self, speed_factor)`

Dynamically adjust movement speed.

**Parameters:**
- `speed_factor` (float): New speed multiplier (must be > 0).

### Methods Starting from Current Position

#### `move_to(self, end_point, seed=None)`

Move from current mouse position to target position.

**Parameters:**
- `end_point` (tuple): Target coordinates (x, y).
- `seed` (int, optional): Random seed for reproducible trajectories.

#### `click_at(self, end_point, seed=None)`

Move from current position to target and perform a single click.

#### `double_click_at(self, end_point, seed=None)`

Move from current position to target and perform a double click.

#### `right_click_at(self, end_point, seed=None)`

Move from current position to target and perform a right click.

#### `drag_to(self, end_point, seed=None)`

Drag from current position to target (press and hold left button).

---

## 🔧 Advanced Usage

### Using Custom Models

If you have a custom-trained model file, you can load it:

```python
controller = HumanMouseController(model_pkl="path/to/your/model.pkl")
```

### Training Your Own Model

For training custom models with your own mouse movement data, please refer to the [GitHub repository](https://github.com/Tomotsugu-dev/HumanMoveMouse) which includes:
- Data collection tools
- Model training scripts
- Complete development environment

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

⚠️ **IMPORTANT NOTICE**

This project is provided for **educational and research purposes only**. By using this software, you agree to the following terms:

1. **Legal Use Only**: This tool must only be used in compliance with all applicable laws and regulations. Users are solely responsible for ensuring their use complies with local, state, federal, and international laws.

2. **No Malicious Use**: This software must NOT be used for any malicious, harmful, or illegal activities, including but not limited to:
   - Unauthorized access to computer systems
   - Circumventing security measures or access controls
   - Creating or distributing malware
   - Violating terms of service of any platform, application, or website
   - Automated interactions with services that prohibit such behavior
   - Any form of fraud, deception, or harassment

3. **User Responsibility**: Users assume full responsibility and liability for their use of this software. The developers and contributors:
   - Are NOT responsible for any misuse or damage caused by this tool
   - Do NOT endorse or encourage any illegal or unethical use
   - Cannot be held liable for any consequences resulting from the use of this software

4. **No Warranty**: This software is provided "AS IS" without warranty of any kind, express or implied. The developers make no guarantees about its:
   - Suitability for any particular purpose
   - Reliability, accuracy, or performance
   - Compatibility with any specific system or application

5. **Ethical Use**: Users are expected to use this tool ethically and responsibly, respecting the rights and privacy of others.

**By using this software, you acknowledge that you have read, understood, and agree to be bound by these terms.**

---

## 🤝 Contributing

Contributions are welcome! Please check out the [GitHub repository](https://github.com/Tomotsugu-dev/HumanMoveMouse) for development setup and guidelines.