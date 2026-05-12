"""
录制事件的 schema 与 JSONL (反)序列化。
Event schema and JSONL (de)serialization for recordings.

每个事件是一个 dict,JSONL 文件中每行一个事件。
Each event is a dict; JSONL files store one event per line.

事件类型 / Event types:
    move:   {"t": float, "type": "move",   "x": int, "y": int}
    click:  {"t": float, "type": "click",  "x": int, "y": int, "button": str, "pressed": bool}
    scroll: {"t": float, "type": "scroll", "x": int, "y": int, "dx": int, "dy": int}
    key:    {"t": float, "type": "key",    "key": str, "pressed": bool}
    meta:   {"t": 0.0,   "type": "meta",   "version": int, "started_at": str}
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Iterable, Iterator

SCHEMA_VERSION = 1

EVENT_MOVE = "move"
EVENT_CLICK = "click"
EVENT_SCROLL = "scroll"
EVENT_KEY = "key"
EVENT_META = "meta"

KNOWN_EVENT_TYPES = frozenset({EVENT_MOVE, EVENT_CLICK, EVENT_SCROLL, EVENT_KEY, EVENT_META})


def write_jsonl(path: str | Path, events: Iterable[dict]) -> None:
    """
    将事件流写入 JSONL 文件。
    Stream events to a JSONL file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev, ensure_ascii=False))
            f.write("\n")


def read_jsonl(path: str | Path) -> list[dict]:
    """
    读取 JSONL 文件;遇未知 type 跳过并 warning。
    Read a JSONL file; unknown event types are skipped with a warning.
    """
    out: list[dict] = []
    for ev in _iter_jsonl(path):
        ev_type = ev.get("type")
        if ev_type not in KNOWN_EVENT_TYPES:
            warnings.warn(f"Skipping unknown event type: {ev_type!r}", stacklevel=2)
            continue
        out.append(ev)
    return out


def _iter_jsonl(path: str | Path) -> Iterator[dict]:
    with Path(path).open("r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                warnings.warn(f"Skipping malformed JSONL at line {line_no}: {e}", stacklevel=2)
