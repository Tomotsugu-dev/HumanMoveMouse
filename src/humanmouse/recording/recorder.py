"""
全局鼠标 + 键盘事件录制器。
Global mouse + keyboard event recorder.

依赖 pynput 监听跨应用的输入事件,时间戳基准是 time.perf_counter() 在 start() 时锁定的 t0。
Uses pynput to listen across-process input; timestamps are relative to t0 captured at start().
"""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pynput import keyboard, mouse

from .schema import (
    EVENT_CLICK,
    EVENT_KEY,
    EVENT_META,
    EVENT_MOVE,
    EVENT_SCROLL,
    SCHEMA_VERSION,
    write_jsonl,
)


class Recorder:
    """
    跨应用录制鼠标/键盘事件,落盘为 JSONL。
    Records mouse/keyboard events across applications, persists as JSONL.

    用法 / Usage:
        rec = Recorder()
        rec.start()
        # ...用户操作 / user activity...
        rec.stop()
        rec.save("session.jsonl")

        # 或上下文管理器 / or context manager:
        with Recorder() as rec:
            time.sleep(10)
        rec.save("session.jsonl")
    """

    DEFAULT_STOP_HOTKEY = "f10"

    def __init__(
        self,
        capture_mouse: bool = True,
        capture_keyboard: bool = True,
        stop_hotkey: Optional[str] = DEFAULT_STOP_HOTKEY,
    ):
        """
        Args:
            capture_mouse:    捕捉鼠标事件 / Capture mouse events.
            capture_keyboard: 捕捉键盘事件 / Capture keyboard events.
            stop_hotkey:      停止录制的按键名(单键),例如 "f10"、"esc";传 None 关闭。
                              Single-key stop hotkey name, e.g. "f10", "esc"; pass None to disable.

        注意:为绕开 pynput 1.8.x 在 macOS 上 GlobalHotKeys 的签名 bug,
        停止键检测合并进主键盘回调,所以只支持"单键",不再支持 "<ctrl>+<f10>" 组合键。
        """
        self.capture_mouse = capture_mouse
        self.capture_keyboard = capture_keyboard
        self.stop_hotkey = stop_hotkey.lower() if stop_hotkey else None

        self._events: list[dict] = []
        self._lock = threading.Lock()
        self._t0: float = 0.0
        self._running = False
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None

    # ---------- 生命周期 / Lifecycle ----------

    def start(self) -> None:
        """启动监听 / Start listeners. Non-blocking."""
        if self._running:
            raise RuntimeError("Recorder is already running")

        with self._lock:
            self._events.clear()
            self._events.append({
                "t": 0.0,
                "type": EVENT_META,
                "version": SCHEMA_VERSION,
                "started_at": datetime.now(timezone.utc).isoformat(),
            })

        self._t0 = time.perf_counter()
        self._running = True

        if self.capture_mouse:
            self._mouse_listener = mouse.Listener(
                on_move=self._on_move,
                on_click=self._on_click,
                on_scroll=self._on_scroll,
            )
            self._mouse_listener.start()

        # 任意需要键盘的场景都启一个 listener:或为捕捉键盘事件,或为检测停止热键。
        # One keyboard listener covers both event capture and stop-hotkey detection.
        if self.capture_keyboard or self.stop_hotkey:
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
            )
            self._keyboard_listener.start()

    def stop(self) -> None:
        """停止监听 / Stop listeners. Idempotent."""
        if not self._running:
            return
        self._running = False

        for listener in (self._mouse_listener, self._keyboard_listener):
            if listener is not None:
                try:
                    listener.stop()
                except Exception:  # noqa: BLE001
                    pass
        self._mouse_listener = None
        self._keyboard_listener = None

    def wait(self, timeout: Optional[float] = None) -> None:
        """
        阻塞直到 stop() 被调用或超时。
        Block until stop() is called or timeout elapses.
        """
        deadline = None if timeout is None else time.perf_counter() + timeout
        while self._running:
            if deadline is not None and time.perf_counter() >= deadline:
                self.stop()
                return
            time.sleep(0.05)

    def __enter__(self) -> "Recorder":
        self.start()
        return self

    def __exit__(self, *exc_info) -> None:
        self.stop()

    # ---------- 数据导出 / Data export ----------

    def events(self) -> list[dict]:
        """返回事件列表的浅拷贝 / Return a shallow copy of the event list."""
        with self._lock:
            return list(self._events)

    def save(self, path: str | Path) -> None:
        """将事件流写入 JSONL / Write the event stream to JSONL."""
        write_jsonl(path, self.events())

    # ---------- 回调 / Callbacks (called from listener threads) ----------

    def _now(self) -> float:
        return time.perf_counter() - self._t0

    def _append(self, ev: dict) -> None:
        with self._lock:
            self._events.append(ev)

    def _on_move(self, x: int, y: int) -> None:
        self._append({"t": self._now(), "type": EVENT_MOVE, "x": int(x), "y": int(y)})

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        self._append({
            "t": self._now(),
            "type": EVENT_CLICK,
            "x": int(x),
            "y": int(y),
            "button": button.name,
            "pressed": bool(pressed),
        })

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        self._append({
            "t": self._now(),
            "type": EVENT_SCROLL,
            "x": int(x),
            "y": int(y),
            "dx": int(dx),
            "dy": int(dy),
        })

    def _on_press(self, key) -> None:
        name = _key_to_str(key)
        # 优先检测停止热键 / Stop hotkey takes precedence.
        if self.stop_hotkey and name.lower() == self.stop_hotkey:
            # 在另一线程触发 stop,避免在 listener 回调里 join 自己的线程。
            # Trigger stop from another thread; can't join the listener thread from within itself.
            threading.Thread(target=self.stop, daemon=True).start()
            return
        if self.capture_keyboard:
            self._append({"t": self._now(), "type": EVENT_KEY, "key": name, "pressed": True})

    def _on_release(self, key) -> None:
        if self.capture_keyboard:
            self._append({
                "t": self._now(),
                "type": EVENT_KEY,
                "key": _key_to_str(key),
                "pressed": False,
            })


def _key_to_str(key) -> str:
    """
    把 pynput Key/KeyCode 序列化成稳定字符串。
    Serialize a pynput Key/KeyCode into a stable string.

    - 常规字符键 → "a", "1", "!"
    - 特殊键(Key.shift 等)→ "shift"
    - 其它 → repr(key) 作为兜底
    """
    if hasattr(key, "char") and key.char is not None:
        return key.char
    if hasattr(key, "name"):
        return key.name
    return repr(key)
