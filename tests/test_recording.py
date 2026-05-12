"""
录制 / 回放的逻辑层测试 — 不真实驱动鼠标。
Recording/playback logic tests — no real mouse activity.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable

import pytest

from humanmouse.recording import player as player_mod
from humanmouse.recording import schema
from humanmouse.recording.player import play_events
from humanmouse.recording.schema import (
    EVENT_CLICK,
    EVENT_KEY,
    EVENT_META,
    EVENT_MOVE,
    EVENT_SCROLL,
    read_jsonl,
    write_jsonl,
)

# ---------- schema 往返 / Schema roundtrip ----------


def test_schema_roundtrip(tmp_path: Path) -> None:
    """写入 JSONL,再读回,应与原列表等价。"""
    events = [
        {"t": 0.0, "type": EVENT_META, "version": 1, "started_at": "2026-05-12T00:00:00+00:00"},
        {"t": 0.016, "type": EVENT_MOVE, "x": 100, "y": 200},
        {"t": 0.123, "type": EVENT_CLICK, "x": 250, "y": 425, "button": "left", "pressed": True},
        {"t": 0.124, "type": EVENT_CLICK, "x": 250, "y": 425, "button": "left", "pressed": False},
        {"t": 0.5, "type": EVENT_SCROLL, "x": 250, "y": 425, "dx": 0, "dy": -1},
        {"t": 1.2, "type": EVENT_KEY, "key": "a", "pressed": True},
        {"t": 1.23, "type": EVENT_KEY, "key": "a", "pressed": False},
    ]
    path = tmp_path / "session.jsonl"
    write_jsonl(path, events)
    roundtrip = read_jsonl(path)
    assert roundtrip == events


def test_schema_skips_unknown_type(tmp_path: Path) -> None:
    """未知 type 应被跳过并发出 warning。"""
    events = [
        {"t": 0.0, "type": EVENT_MOVE, "x": 1, "y": 2},
        {"t": 0.1, "type": "future_event_v9000", "payload": "???"},
        {"t": 0.2, "type": EVENT_MOVE, "x": 3, "y": 4},
    ]
    path = tmp_path / "mixed.jsonl"
    write_jsonl(path, events)
    with pytest.warns(UserWarning, match="future_event_v9000"):
        out = read_jsonl(path)
    assert len(out) == 2
    assert out[0]["x"] == 1
    assert out[1]["x"] == 3


def test_schema_skips_malformed_line(tmp_path: Path) -> None:
    """半截 JSON 应被跳过并发出 warning。"""
    path = tmp_path / "bad.jsonl"
    path.write_text(
        '{"t":0.0,"type":"move","x":1,"y":2}\n'
        '{not json at all\n'
        '{"t":0.1,"type":"move","x":3,"y":4}\n',
        encoding="utf-8",
    )
    with pytest.warns(UserWarning, match="malformed"):
        out = read_jsonl(path)
    assert len(out) == 2


# ---------- player 分派 / Player dispatch ----------


@pytest.fixture
def fake_pyautogui(monkeypatch: pytest.MonkeyPatch) -> dict[str, list]:
    """把 player 用到的 pyautogui 函数全部替换为记录调用的 stub。"""
    calls: dict[str, list] = {
        "moveTo": [], "mouseDown": [], "mouseUp": [],
        "scroll": [], "keyDown": [], "keyUp": [],
    }
    for name in calls:
        monkeypatch.setattr(player_mod.pyautogui, name, lambda *a, _n=name, **kw: calls[_n].append((a, kw)))
    # _configure_pyautogui 调用的属性也设上,避免赋值时报错
    monkeypatch.setattr(player_mod.pyautogui, "MINIMUM_DURATION", 0.0, raising=False)
    monkeypatch.setattr(player_mod.pyautogui, "MINIMUM_SLEEP", 0.0, raising=False)
    monkeypatch.setattr(player_mod.pyautogui, "PAUSE", 0.0, raising=False)
    return calls


def test_dispatch_all_event_types(fake_pyautogui: dict[str, list]) -> None:
    """各类事件应路由到正确的 pyautogui 调用。"""
    events = [
        {"t": 0.0, "type": EVENT_META, "version": 1, "started_at": "x"},
        {"t": 0.0, "type": EVENT_MOVE, "x": 100, "y": 200},
        {"t": 0.0, "type": EVENT_CLICK, "x": 50, "y": 60, "button": "left", "pressed": True},
        {"t": 0.0, "type": EVENT_CLICK, "x": 50, "y": 60, "button": "right", "pressed": False},
        {"t": 0.0, "type": EVENT_SCROLL, "x": 10, "y": 20, "dx": 0, "dy": 3},
        {"t": 0.0, "type": EVENT_KEY, "key": "a", "pressed": True},
        {"t": 0.0, "type": EVENT_KEY, "key": "a", "pressed": False},
    ]
    play_events(events, clock=lambda: 0.0, sleep=lambda _s: None, abort_key=None)

    assert fake_pyautogui["moveTo"] == [((100, 200), {"duration": 0})]
    assert fake_pyautogui["mouseDown"] == [((50, 60), {"button": "left"})]
    assert fake_pyautogui["mouseUp"] == [((50, 60), {"button": "right"})]
    assert fake_pyautogui["scroll"] == [((3,), {"x": 10, "y": 20})]
    assert fake_pyautogui["keyDown"] == [(("a",), {})]
    assert fake_pyautogui["keyUp"] == [(("a",), {})]


# ---------- player 时序 / Player scheduling ----------


class _FakeClock:
    """可注入的虚拟时钟 + sleep,记录所有 sleep 时长。"""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def tick(self, dt: float) -> None:
        self.now += dt

    def __call__(self) -> float:
        return self.now

    def sleep(self, duration: float) -> None:
        self.sleeps.append(duration)
        self.now += duration


def test_scheduling_uses_absolute_targets(fake_pyautogui: dict[str, list]) -> None:
    """player 应基于绝对时间调度;sleep 时长之和 = 最后事件的 t。"""
    clock = _FakeClock()
    events = [
        {"t": 0.0, "type": EVENT_MOVE, "x": 1, "y": 1},
        {"t": 0.1, "type": EVENT_MOVE, "x": 2, "y": 2},
        {"t": 0.3, "type": EVENT_MOVE, "x": 3, "y": 3},
    ]
    play_events(events, clock=clock, sleep=clock.sleep, abort_key=None)
    assert pytest.approx(sum(clock.sleeps), abs=1e-9) == 0.3
    assert len(fake_pyautogui["moveTo"]) == 3


def test_scheduling_is_drift_free(fake_pyautogui: dict[str, list]) -> None:
    """
    如果某个 dispatch 模拟为"额外耗时",下一段 sleep 应自动压缩;总耗时仍贴近最后事件 t。
    Drift-free: a slow dispatch should shrink the next sleep, not push everything back.
    """
    clock = _FakeClock()

    # 让第一次 moveTo 模拟"耗时 0.15s",远长于事件间隔 0.1s
    original_move = player_mod.pyautogui.moveTo
    call_count = {"n": 0}

    def slow_move(*args, **kwargs) -> None:
        call_count["n"] += 1
        if call_count["n"] == 1:
            clock.tick(0.15)  # 第一次额外消耗 0.15s
        original_move(*args, **kwargs)

    player_mod.pyautogui.moveTo = slow_move
    try:
        events = [
            {"t": 0.0, "type": EVENT_MOVE, "x": 1, "y": 1},
            {"t": 0.1, "type": EVENT_MOVE, "x": 2, "y": 2},  # 目标 0.1s,但第一次拖到 0.15s
            {"t": 0.3, "type": EVENT_MOVE, "x": 3, "y": 3},  # 这次应只 sleep 0.15s 而非 0.2s
        ]
        play_events(events, clock=clock, sleep=clock.sleep, abort_key=None)
    finally:
        player_mod.pyautogui.moveTo = original_move

    # 关键断言:总耗时贴最后事件 t=0.3s,允许小误差;若漂移会变 0.35+
    assert pytest.approx(clock.now, abs=1e-9) == 0.3


def test_speed_compresses_timeline(fake_pyautogui: dict[str, list]) -> None:
    """speed=2 时总耗时应减半。"""
    clock = _FakeClock()
    events = [
        {"t": 0.0, "type": EVENT_MOVE, "x": 1, "y": 1},
        {"t": 1.0, "type": EVENT_MOVE, "x": 2, "y": 2},
    ]
    play_events(events, speed=2.0, clock=clock, sleep=clock.sleep, abort_key=None)
    assert pytest.approx(clock.now, abs=1e-9) == 0.5


def test_invalid_speed_rejected() -> None:
    with pytest.raises(ValueError, match="speed"):
        play_events([], speed=0.0, abort_key=None)


# ---------- recorder 基本生命周期 / Recorder lifecycle ----------


def test_recorder_lifecycle_no_listeners() -> None:
    """禁用所有监听 + 热键时,start/stop/save 应都不炸。"""
    from humanmouse.recording import Recorder

    rec = Recorder(capture_mouse=False, capture_keyboard=False, stop_hotkey=None)
    rec.start()
    rec.stop()
    events = rec.events()
    # 应只有 meta 头 / Only the meta header.
    assert len(events) == 1
    assert events[0]["type"] == EVENT_META


def test_recorder_double_start_rejected() -> None:
    from humanmouse.recording import Recorder

    rec = Recorder(capture_mouse=False, capture_keyboard=False, stop_hotkey=None)
    rec.start()
    try:
        with pytest.raises(RuntimeError):
            rec.start()
    finally:
        rec.stop()


def test_recorder_stop_hotkey_triggers_stop_without_capturing_keys() -> None:
    """stop_hotkey 应在 capture_keyboard=False 时仍生效,且不留下键盘事件。"""
    from humanmouse.recording import Recorder

    rec = Recorder(capture_mouse=False, capture_keyboard=False, stop_hotkey="f10")
    rec.start()
    try:
        # 模拟 listener 回调里收到 F10
        class _FakeKey:
            name = "f10"

        rec._on_press(_FakeKey())  # 触发停止 + 不应追加事件
        # stop() 在 daemon 线程里被调用,等一下让它执行完
        import time as _time
        for _ in range(50):
            if not rec._running:
                break
            _time.sleep(0.02)
        assert not rec._running
        # 事件列表只该有 meta 头
        events = rec.events()
        assert len(events) == 1 and events[0]["type"] == EVENT_META
    finally:
        rec.stop()


def test_recorder_keyboard_event_recorded_when_not_stop_key() -> None:
    """普通键(非 stop_hotkey)应被记录。"""
    from humanmouse.recording import Recorder

    rec = Recorder(capture_mouse=False, capture_keyboard=True, stop_hotkey="f10")
    rec.start()
    try:
        class _A:
            char = "a"
            name = None

        rec._on_press(_A())
        rec._on_release(_A())
        events = rec.events()
        # meta + press + release
        assert len(events) == 3
        assert events[1] == {**events[1], "type": EVENT_KEY, "key": "a", "pressed": True}
        assert events[2] == {**events[2], "type": EVENT_KEY, "key": "a", "pressed": False}
    finally:
        rec.stop()
