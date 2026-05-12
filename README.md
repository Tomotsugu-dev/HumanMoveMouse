# HumanMoveMouse 🖱️

![PyPI](https://img.shields.io/pypi/v/humanmovemouse)[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

🎯 **Python 鼠标自动化工具:仿人类轨迹移动、像素精确直线移动、跨应用录制与精确回放。**
🎯 **Python mouse automation: human-like trajectories, pixel-exact straight moves, and global record / precise replay.**

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
  - [Basic Mouse Actions](#basic-mouse-actions)
  - [From Current Position](#from-current-position)
  - [Customizing Movement](#customizing-movement)
  - [Straight-Line Mode](#straight-line-mode)
  - [Recording](#recording)
  - [Playback](#playback)
- [🖥️ Command Line](#%EF%B8%8F-command-line)
- [📖 API Reference](#-api-reference)
  - [HumanMouseController](#humanmousecontroller)
  - [Methods Starting from Current Position](#methods-starting-from-current-position)
  - [Recorder](#recorder)
  - [Playback Functions](#playback-functions)
  - [Utilities](#utilities)
- [🔧 Advanced](#-advanced)
  - [Custom Models](#custom-models)
  - [Training Your Own Model](#training-your-own-model)
  - [Project Layout](#project-layout)
- [⚠️ Platform Notes](#%EF%B8%8F-platform-notes)
- [📄 License](#-license)
- [⚠️ Disclaimer](#%EF%B8%8F-disclaimer)
- [🤝 Contributing](#-contributing)

---

## ✨ Features

- **Human-like trajectories** — smooth, naturalistic mouse paths suitable for UI testing, demos, or behavior simulation.
- **Pixel-exact straight-line mode** — bypass the human model when you need precise endpoints (e.g. clicking small UI targets).
- **All common mouse actions** — move, click, double-click, right-click, drag.
- **Move from current cursor position** — `move_to`, `click_at`, `double_click_at`, `right_click_at`, `drag_to`.
- **Adjustable speed / smoothness / jitter** — `speed_factor`, `num_points`, `jitter_amplitude`.
- **Reproducible paths** — pass `seed` to regenerate the exact same trajectory.
- **Cross-application recording** — capture global mouse + keyboard events to a portable JSONL file.
- **Precise playback** — replay recordings byte-for-byte with the original timing; supports speed scaling, looping, and abort hotkey.
- **CLI included** — `humanmouse move / click / drag / record / play`.
- **Pre-trained model bundled** — works out of the box, no setup required.

### 🎬 Demo

<div align="center">

https://github.com/user-attachments/assets/55e5e295-bb93-4122-b4de-63380c4d1b13

</div>

---

## 📦 Installation

Install from PyPI:

```bash
pip install HumanMoveMouse
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add HumanMoveMouse
```

### From source (development)

```bash
git clone https://github.com/Tomotsugu-dev/HumanMoveMouse
cd HumanMoveMouse
uv sync                 # creates .venv + installs deps + the package in editable mode
# or:
pip install -e ".[dev]"
```

Optional extras:

- `humanmouse[collector]` — adds `pygame`, required only for running the trajectory collector under [csv_data_collector/](csv_data_collector/).
- `humanmouse[dev]` — adds `pytest` and `pygame` for tests + dev workflows.

---

## 🚀 Quick Start

### Basic Mouse Actions

```python
from humanmouse import HumanMouseController

controller = HumanMouseController()

controller.move((100, 100), (800, 600))                       # Move
controller.move_and_click((100, 100), (400, 400))             # Move + left click
controller.move_and_double_click((400, 400), (600, 300))      # Move + double click
controller.move_and_right_click((600, 300), (800, 500))       # Move + right click
controller.drag((300, 300), (500, 500))                       # Drag
```

### From Current Position

These shortcuts read the live cursor location and use it as the start point:

```python
controller.move_to((800, 600))
controller.click_at((400, 400))
controller.double_click_at((600, 300))
controller.right_click_at((500, 500))
controller.drag_to((300, 300))
```

### Customizing Movement

```python
controller = HumanMouseController(
    num_points=200,           # More points = smoother
    jitter_amplitude=0.2,     # Less jitter = straighter, calmer path
    speed_factor=0.5,         # <1 slower, >1 faster
)

# Adjust speed dynamically:
controller.set_speed(2.0)     # 2x speed
controller.set_speed(0.5)     # half speed
```

### Straight-Line Mode

Need pixel-exact endpoints with no curvature and no jitter — useful for clicking
small UI targets:

```python
# Enable at construction
controller = HumanMouseController(straight=True, speed_factor=2.0)
controller.move_to((250, 425))   # Pixel-exact endpoint

# Or flip on an existing controller
controller.straight = True
controller.click_at((1024, 768))
```

Straight mode ignores `jitter_amplitude` and `seed`. Baseline speed is
`HumanMouseController.STRAIGHT_PX_PER_SEC` (default 1500 px/s), further scaled
by `speed_factor`.

### Recording

Capture global mouse + keyboard events across any application to a JSONL file:

```python
from humanmouse import Recorder

# Programmatic
rec = Recorder()
rec.start()
rec.wait(timeout=10)         # block 10s, or rec.stop() from another thread
rec.save("session.jsonl")

# Context manager
with Recorder() as rec:
    rec.wait(timeout=10)
rec.save("session.jsonl")

# Mouse only, custom stop hotkey
rec = Recorder(capture_keyboard=False, stop_hotkey="esc")
rec.start()
rec.wait()                   # waits until Esc is pressed
rec.save("mouse_only.jsonl")
```

### Playback

Replay a recording with original timing (or scaled). Press **Esc** during
playback to abort.

```python
from humanmouse import play_file

play_file("session.jsonl")                        # 1x speed, once
play_file("session.jsonl", speed=3.0)             # 3x faster
play_file("session.jsonl", loop=5)                # repeat 5 times
play_file("session.jsonl", abort_key=None)        # disable abort hotkey
```

---

## 🖥️ Command Line

The `humanmouse` console script is installed automatically.

```bash
# Move / click / drag (uses live cursor as start point)
humanmouse move  --to 800 600 --speed 2.0
humanmouse click --at 500 400
humanmouse click --at 500 400 --button right
humanmouse click --at 500 400 --double
humanmouse drag  --from 100 100 --to 800 600

# Record (press F10 to stop; or set --duration)
humanmouse record session.jsonl
humanmouse record session.jsonl --no-keyboard
humanmouse record session.jsonl --duration 30
humanmouse record session.jsonl --stop-key esc

# Replay (press Esc to abort)
humanmouse play  session.jsonl
humanmouse play  session.jsonl --speed 2.0 --loop 3
humanmouse play  session.jsonl --abort-key ''      # disable abort key
```

---

## 📖 API Reference

### HumanMouseController

#### `__init__(model_pkl=None, num_points=100, jitter_amplitude=0.3, speed_factor=1.0, straight=False)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model_pkl` | `str \| None` | `None` | Path to a custom model file. `None` uses the bundled model. |
| `num_points` | `int` | `100` | Number of trajectory points. Higher = smoother. |
| `jitter_amplitude` | `float` | `0.3` | Random jitter magnitude in pixels. `0` disables. Ignored when `straight=True`. |
| `speed_factor` | `float` | `1.0` | Speed multiplier. `>1` faster, `<1` slower. |
| `straight` | `bool` | `False` | If `True`, move in a strict straight line with exact endpoints. |

#### Movement methods (explicit start point)

| Method | Effect |
|---|---|
| `move(start, end, seed=None)` | Move from `start` to `end`. |
| `move_and_click(start, end, seed=None)` | Move then left-click. |
| `move_and_double_click(start, end, seed=None)` | Move then double-click. |
| `move_and_right_click(start, end, seed=None)` | Move then right-click. |
| `drag(start, end, seed=None)` | Press left button, drag from `start` to `end`, release. |

`start` and `end` are `(x, y)` tuples. Pass `seed` (int) for a reproducible trajectory.

#### `set_speed(speed_factor)`

Change speed at runtime. Must be `> 0`.

```python
controller.set_speed(2.0)
```

### Methods Starting from Current Position

These read the live cursor position and use it as `start`:

| Method | Effect |
|---|---|
| `move_to(end, seed=None)` | Move to `end`. |
| `click_at(end, seed=None)` | Move to `end` and left-click. |
| `double_click_at(end, seed=None)` | Move to `end` and double-click. |
| `right_click_at(end, seed=None)` | Move to `end` and right-click. |
| `drag_to(end, seed=None)` | Drag from current position to `end`. |

#### `create_controller(**kwargs)` (factory)

```python
from humanmouse import create_controller
controller = create_controller(straight=True, speed_factor=2.0)
```

Equivalent to `HumanMouseController(**kwargs)`.

### Recorder

```python
from humanmouse import Recorder
```

#### `Recorder(capture_mouse=True, capture_keyboard=True, stop_hotkey="f10")`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `capture_mouse` | `bool` | `True` | Capture move / click / scroll events. |
| `capture_keyboard` | `bool` | `True` | Capture key press / release events. |
| `stop_hotkey` | `str \| None` | `"f10"` | Single-key name that stops recording. Pass `None` to disable. |

#### Methods

| Method | Description |
|---|---|
| `start()` | Begin listening. Non-blocking. Raises `RuntimeError` if already running. |
| `stop()` | Stop listening. Idempotent. |
| `wait(timeout=None)` | Block until `stop()` is called or `timeout` seconds elapse. |
| `events()` | Return a shallow copy of the captured event list. |
| `save(path)` | Write captured events to a JSONL file. |

`Recorder` is also a context manager:

```python
with Recorder() as rec:
    rec.wait(timeout=10)
rec.save("session.jsonl")
```

### Playback Functions

```python
from humanmouse import play_file, play_events
```

#### `play_file(path, speed=1.0, loop=1, abort_key="esc")`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str` | — | JSONL recording path. |
| `speed` | `float` | `1.0` | Playback speed multiplier. |
| `loop` | `int` | `1` | Number of times to play. |
| `abort_key` | `str \| None` | `"esc"` | Single-key name to abort. Pass `None` to disable. |

#### `play_events(events, speed=1.0, abort_key="esc")`

Same as `play_file` but takes a list of event dicts (already deserialized).

### Utilities

```python
from humanmouse.utils import track_mouse_position
track_mouse_position(duration=30)   # live-print cursor position for 30s
```

#### File format (JSONL)

One JSON event per line. `t` is seconds from session start.

```jsonc
{"t":0.000,"type":"meta","version":1,"started_at":"2026-05-12T12:00:00+00:00"}
{"t":0.016,"type":"move",  "x":100,"y":200}
{"t":0.123,"type":"click", "x":250,"y":425,"button":"left","pressed":true}
{"t":0.124,"type":"click", "x":250,"y":425,"button":"left","pressed":false}
{"t":0.500,"type":"scroll","x":250,"y":425,"dx":0,"dy":-1}
{"t":1.200,"type":"key",   "key":"a","pressed":true}
{"t":1.230,"type":"key",   "key":"a","pressed":false}
```

| Type | Fields |
|---|---|
| `meta` | `version` (int), `started_at` (ISO-8601) |
| `move` | `x`, `y` |
| `click` | `x`, `y`, `button` (`"left"`/`"right"`/`"middle"`), `pressed` (bool) |
| `scroll` | `x`, `y`, `dx`, `dy` (only `dy` is replayed) |
| `key` | `key` (str), `pressed` (bool) |

You can also read/write JSONL recordings directly:

```python
from humanmouse.recording import read_jsonl, write_jsonl
events = read_jsonl("session.jsonl")
write_jsonl("session.jsonl", events)
```

---

## 🔧 Advanced

### Custom Models

Load your own trained model file:

```python
controller = HumanMouseController(model_pkl="path/to/your/model.pkl")
```

### Training Your Own Model

```bash
# 1. Collect samples (saves CSVs into csv_data/). Needs the [collector] extra.
uv run python csv_data_collector/mouse_trajectory_collector.py

# 2. Re-train the bundled model from csv_data/
uv run python scripts/train_model.py
```

### Project Layout

```text
src/humanmouse/
  __init__.py            # Public API: HumanMouseController, Recorder, play_file, ...
  cli.py                 # humanmouse console script
  controllers/           # HumanMouseController
  models/
    data/mouse_model.pkl # Bundled, pre-trained model
  recording/             # Recorder + player + JSONL schema
  utils/                 # track_mouse_position
csv_data/                # Recorded training trajectories
csv_data_collector/      # Pygame app to record more trajectories
demos/                   # Runnable demo scripts
scripts/train_model.py   # Re-train the bundled model from csv_data/
tests/                   # pytest test suite
```

### Running tests

```bash
uv run pytest
```

---

## ⚠️ Platform Notes

- **macOS**: The first run will receive zero events until you grant Accessibility
  permission to your terminal / Python interpreter at
  *System Settings → Privacy & Security → Accessibility*. Restart the terminal
  after granting.
- **Linux**: Works on X11. Wayland support in the underlying input library is limited.
- **Replay coordinate caveat**: Coordinates are absolute pixels. If screen
  resolution, DPI, or target window positions differ between recording and
  replay, the playback will hit the wrong locations even though timing is exact.
- **Horizontal scroll** (`dx`): captured but ignored on playback (the playback
  backend only supports vertical scrolling).

---

## 📄 License

Licensed under the MIT License — see [LICENSE](LICENSE) for details.

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

Contributions are welcome! Please open an issue or PR on the [GitHub repository](https://github.com/Tomotsugu-dev/HumanMoveMouse).
