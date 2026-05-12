"""
命令行接口
Command-line interface for HumanMouse.
"""
import argparse
import sys
from typing import Optional, Sequence

import pyautogui

from .__version__ import __version__
from .controllers.mouse_controller import HumanMouseController
from .recording import Recorder, play_file


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="humanmouse",
        description="Human-like mouse movement automation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  humanmouse move --to 800 600\n"
            "  humanmouse click --at 500 400\n"
            "  humanmouse drag --from 100 100 --to 800 600\n"
            "  humanmouse move --to 800 600 --speed 2.0\n"
            "  humanmouse record session.jsonl                 # F10 to stop\n"
            "  humanmouse play   session.jsonl --speed 2.0\n"
        ),
    )
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s {__version__}"
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # --- move ---
    move_p = sub.add_parser("move", help="Move mouse to position")
    move_p.add_argument("--to", nargs=2, type=int, required=True, metavar=("X", "Y"))
    move_p.add_argument("--speed", type=float, default=1.0)

    # --- click ---
    click_p = sub.add_parser("click", help="Move and click at position")
    click_p.add_argument("--at", nargs=2, type=int, required=True, metavar=("X", "Y"))
    click_p.add_argument(
        "--button", choices=["left", "right", "middle"], default="left"
    )
    click_p.add_argument("--double", action="store_true")
    click_p.add_argument("--speed", type=float, default=1.0)

    # --- drag ---
    drag_p = sub.add_parser("drag", help="Drag from one position to another")
    drag_p.add_argument(
        "--from", nargs=2, type=int, required=True, metavar=("X", "Y"), dest="from_"
    )
    drag_p.add_argument("--to", nargs=2, type=int, required=True, metavar=("X", "Y"))
    drag_p.add_argument("--speed", type=float, default=1.0)

    # --- record ---
    rec_p = sub.add_parser("record", help="Record mouse + keyboard events to JSONL")
    rec_p.add_argument("output", help="Output JSONL path")
    rec_p.add_argument(
        "--no-mouse", action="store_true", help="Skip mouse events"
    )
    rec_p.add_argument(
        "--no-keyboard", action="store_true", help="Skip keyboard events"
    )
    rec_p.add_argument(
        "--duration", type=float, default=None,
        help="Auto-stop after N seconds (default: wait for F10)",
    )
    rec_p.add_argument(
        "--stop-key", default="f10",
        help="Single-key stop hotkey name (default: f10). Examples: f10, esc",
    )

    # --- play ---
    play_p = sub.add_parser("play", help="Replay a JSONL recording")
    play_p.add_argument("input", help="Recording JSONL path")
    play_p.add_argument(
        "--speed", type=float, default=1.0, help="Playback speed multiplier"
    )
    play_p.add_argument(
        "--loop", type=int, default=1, help="Number of times to loop"
    )
    play_p.add_argument(
        "--abort-key", default="esc",
        help="Abort hotkey name (default: esc); pass '' to disable",
    )

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    主命令行入口
    Main command-line entry point.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "record":
            return _cmd_record(args)
        if args.command == "play":
            return _cmd_play(args)

        controller = HumanMouseController()
        controller.set_speed(args.speed)
        current = pyautogui.position()
        start = (current.x, current.y)

        if args.command == "move":
            controller.move(start, tuple(args.to))
        elif args.command == "click":
            target = tuple(args.at)
            if args.double:
                controller.move_and_double_click(start, target)
            elif args.button == "right":
                controller.move_and_right_click(start, target)
            else:
                controller.move_and_click(start, target)
        elif args.command == "drag":
            from_pt = tuple(args.from_)
            controller.move(start, from_pt)
            controller.drag(from_pt, tuple(args.to))

        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _cmd_record(args: argparse.Namespace) -> int:
    rec = Recorder(
        capture_mouse=not args.no_mouse,
        capture_keyboard=not args.no_keyboard,
        stop_hotkey=args.stop_key or None,
    )
    print(f"Recording to {args.output} ...")
    if args.duration:
        print(f"  Auto-stop after {args.duration:.1f}s.")
    else:
        print(f"  Press {args.stop_key} to stop.")
    rec.start()
    try:
        rec.wait(timeout=args.duration)
    except KeyboardInterrupt:
        rec.stop()
    rec.save(args.output)
    n = sum(1 for _ in rec.events()) - 1  # 减去 meta 头 / minus meta header
    print(f"Saved {n} events to {args.output}")
    return 0


def _cmd_play(args: argparse.Namespace) -> int:
    abort = args.abort_key or None
    print(f"Playing {args.input} at speed={args.speed}x, loop={args.loop} ...")
    if abort:
        print(f"  Press {abort} to abort.")
    play_file(args.input, speed=args.speed, loop=args.loop, abort_key=abort)
    print("Playback finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
