# mouse_utils/position_tracker.py
import pyautogui
import time

def track_mouse_position(duration: int = 10):
    """
    在指定的时间内持续追踪并显示鼠标坐标。
    Continuously tracks and displays the mouse coordinates for a specified duration.

    Args:
        duration (int): 追踪持续的秒数。
                        The duration in seconds for which to track.
    """
    print(f"Mouse position tracker will run for {duration} seconds.")
    print("Press Ctrl-C to quit early.")
    
    start_time = time.time()
    try:
        while (time.time() - start_time) < duration:
            # 获取当前鼠标坐标
            # Get the current mouse coordinates
            x, y = pyautogui.position()
            
            # 格式化位置字符串
            # Format the position string
            position_str = f"X: {str(x).rjust(4)} Y: {str(y).rjust(4)}"
            
            # 打印字符串，覆盖前一行
            # Print the string, overwriting the previous line
            print(position_str, end='\r')
            
            # 短暂延迟以防止CPU占用过高
            # A small delay to prevent high CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        # 允许用户提前退出
        # Allow the user to quit early
        pass 
    
    # 清理行尾
    # Clean up the end of the line
    print("\nTracker finished." + " "*20) 

# 这个部分允许此脚本也能独立运行进行测试
# This part allows the script to be run standalone for testing
if __name__ == '__main__':
    # 独立运行时，追踪15秒
    # When run independently, track for 15 seconds
    track_mouse_position(15)