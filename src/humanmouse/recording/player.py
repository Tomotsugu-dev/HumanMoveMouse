"""
录制文件回放器:无漂移时序调度 + 事件分派给 pyautogui。
Recording player: drift-free scheduling + pyautogui dispatch.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable, Optional

import pyautogui
from pynput import keyboard

from ..controllers.mouse_controller import _configure_pyautogui
from .schema import EVENT_CLICK, EVENT_KEY, EVENT_META, EVENT_MOVE, EVENT_SCROLL, read_jsonl

# 类型别名:获取"当前时间"的可调用对象,测试时可替换为 fake 时钟。
# Type alias for a "now()" callable; tests may substitute a fake clock.
Clock = Callable[[], float]


def play_file(
    path: str | Path,
    speed: float = 1.0,
    loop: int = 1,
    abort_key: Optional[str] = "esc",
) -> None:
    """
    从 JSONL 文件回放录制。
    Play a recorded session from a JSONL file.

    Args:
        path:      录制文件路径 / Recording file path.
        speed:     回放速度倍率 / Playback speed multiplier (>1 = faster).
        loop:      循环次数 / Number of times to loop. Default 1.
        abort_key: 中断热键(pynput 名,如 "esc");传 None 关闭。
                   Abort hotkey (pynput name, e.g. "esc"); pass None to disable.
    """
    events = read_jsonl(path)
    for _ in range(max(1, loop)):
        play_events(events, speed=speed, abort_key=abort_key)


def play_events(
    events: list[dict],
    speed: float = 1.0,
    abort_key: Optional[str] = "esc",
    clock: Optional[Clock] = None,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """
    回放一段事件列表,使用绝对时间调度避免漂移累积。
    Replay an event list using absolute-time scheduling to avoid drift.

    Args:
        events:    事件列表 / Event list. 必须按 t 单调递增 / must be t-monotonic.
        speed:     回放速度倍率 / Speed multiplier.
        abort_key: 中断热键名 / Abort hotkey name; None disables.
        clock:     注入的 now() 时钟,默认 time.perf_counter(测试用)。
                   Injected now() clock, defaults to time.perf_counter (for tests).
        sleep:     注入的 sleep 函数,默认 time.sleep(测试用)。
                   Injected sleep, defaults to time.sleep (for tests).
    """
    if speed <= 0:
        raise ValueError("speed must be > 0")

    _configure_pyautogui()
    clock = clock or time.perf_counter

    stop_event = threading.Event()
    listener = _start_abort_listener(abort_key, stop_event) if abort_key else None

    try:
        t0 = clock()
        for ev in events:
            if stop_event.is_set():
                return
            target = t0 + float(ev.get("t", 0.0)) / speed
            delay = target - clock()
            if delay > 0:
                # 拆分 sleep 以便中断时尽快响应 / Chunk sleep so we can react to abort quickly.
                _interruptible_sleep(delay, stop_event, sleep)
            if stop_event.is_set():
                return
            _dispatch(ev)
    finally:
        if listener is not None:
            listener.stop()


# ---------- 内部 / Internal ----------


def _dispatch(ev: dict) -> None:
    """把单个事件翻译成 pyautogui 调用 / Translate a single event into a pyautogui call."""
    ev_type = ev.get("type")
    if ev_type == EVENT_META:
        return
    if ev_type == EVENT_MOVE:
        pyautogui.moveTo(ev["x"], ev["y"], duration=0)
    elif ev_type == EVENT_CLICK:
        if ev["pressed"]:
            pyautogui.mouseDown(ev["x"], ev["y"], button=ev["button"])
        else:
            pyautogui.mouseUp(ev["x"], ev["y"], button=ev["button"])
    elif ev_type == EVENT_SCROLL:
        # pyautogui.scroll 只支持垂直,dx 被忽略 / Only vertical supported.
        pyautogui.scroll(int(ev["dy"]), x=ev["x"], y=ev["y"])
    elif ev_type == EVENT_KEY:
        if ev["pressed"]:
            pyautogui.keyDown(ev["key"])
        else:
            pyautogui.keyUp(ev["key"])
    # 未知类型已被 read_jsonl 过滤;此处静默忽略以容错
    # Unknown types were filtered by read_jsonl; ignored here defensively.


def _interruptible_sleep(
    duration: float,
    stop_event: threading.Event,
    sleep: Callable[[float], None],
    chunk: float = 0.05,
) -> None:
    """
    分块 sleep,在停止信号到来时尽快返回。
    Chunked sleep that yields promptly when stop_event is set.
    """
    remaining = duration
    while remaining > 0 and not stop_event.is_set():
        step = chunk if remaining > chunk else remaining
        sleep(step)
        remaining -= step


def _start_abort_listener(
    abort_key: str, stop_event: threading.Event
) -> keyboard.Listener:
    """
    起一个 daemon 线程监听 abort_key,按下即 set stop_event。
    Start a daemon thread listening for abort_key; set stop_event on press.
    """
    target = abort_key.lower()

    def on_press(key) -> None:
        name = getattr(key, "name", None) or getattr(key, "char", None)
        if isinstance(name, str) and name.lower() == target:
            stop_event.set()

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    return listener
