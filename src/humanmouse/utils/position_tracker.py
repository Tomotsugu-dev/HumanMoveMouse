"""
实时鼠标坐标追踪工具
Real-time mouse position tracker.
"""
import time

import pyautogui


def track_mouse_position(duration: int = 10) -> None:
    """
    在指定的时间内持续追踪并显示鼠标坐标。
    Continuously tracks and displays the mouse coordinates for a specified duration.

    Args:
        duration: 追踪持续的秒数 / Duration in seconds.
    """
    print(f"Mouse position tracker will run for {duration} seconds.")
    print("Press Ctrl-C to quit early.")

    start_time = time.time()
    try:
        while (time.time() - start_time) < duration:
            # 获取当前鼠标坐标 / Get the current mouse coordinates
            x, y = pyautogui.position()
            position_str = f"X: {str(x).rjust(4)} Y: {str(y).rjust(4)}"
            # 覆盖前一行 / Overwrite the previous line
            print(position_str, end="\r")
            # 短暂延迟以防止CPU占用过高 / Small delay to avoid CPU spin
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    print("\nTracker finished." + " " * 20)


if __name__ == "__main__":
    track_mouse_position(120)
