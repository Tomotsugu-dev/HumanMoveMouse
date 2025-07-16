"""
Mouse Trajectory Collecter.py

Description:
    A Pygame-based application that presents the user with a green “START” circle
    and a red “END” circle placed randomly on the screen. The user must click and
    hold the left mouse button inside the start circle, drag the cursor to the end
    circle, and release inside the end circle. While dragging, the program records
    the mouse trajectory (x, y) along with the timestamp intervals between samples.
    Upon successful completion, the trajectory data is saved as a CSV file, and
    summary statistics (total time, total distance, average speed) are printed.

Creation Date:
    2025-07-15

Dependencies:
    • Python Standard Library:
        – random       (for random coordinate generation)
        – time         (to timestamp trajectory samples)
        – csv          (to write trajectory data to CSV)
        – hashlib      (to generate unique file hashes)
        – datetime     (to timestamp file naming)
    • Third-Party:
        – pygame       (for graphical interface and event handling)

Usage:
    1. Ensure pygame is installed: `pip install pygame`
    2. Run the script: `python mouse_tracking_game.py`
    3. Follow on-screen instructions:
       • Press and hold left mouse button in the green circle to start recording.
       • Drag cursor to the red circle while holding the button.
       • Release the button inside the red circle to finish and save data.
       • Press “R” to regenerate start/end points before starting.
       • After completion, press “SPACE” to reset and play again.
       • Close the window or press the window’s close button to exit.

Key Classes & Methods:
    class MouseTrackingGame:
        • __init__: Initialize Pygame, window, colors, fonts, and generate points.
        • generate_points: Randomly positions start/end circles with minimum separation.
        • is_point_near_target: Checks whether a given (x, y) is within a target radius.
        • start_tracking: Begins trajectory capture, recording start time and position.
        • record_mouse_position: Appends current cursor position and inter-sample time.
        • finish_game: Ends tracking, stores final position, and triggers save_trajectory.
        • save_trajectory: Writes the trajectory to a uniquely named CSV and prints stats.
        • draw: Renders all game elements, from start/end circles to trajectory lines.
        • fail_and_reset: Aborts current run if the user releases outside the end circle.
        • reset_game: Resets state and generates a new pair of points.
        • run: Main loop handling Pygame events, updating state, and redrawing interface.

Data Output:
    • CSV filename format: X{start_x}Y{start_y}_X{end_x}Y{end_y}_{hash}.csv
      where `{hash}` is an 8-character MD5 digest based on timestamp and trajectory length.
    • CSV columns: x_coordinate, y_coordinate, time_interval_seconds
    • Console prints: file path, number of samples, total time (s), total distance (pixels),
      average speed (pixels/s).

Notes:
    • Minimum start/end separation ensures meaningful trajectories.
    • Time intervals are computed relative to the last recorded sample.
    • On failure (wrong release), the game resets without saving data.
    
-------------------------------------------------------------------------------
Mouse Trajectory Collecter.py

描述：
    这是一个基于 Pygame 的应用程序，屏幕上随机放置一个绿色的“开始”圆圈和一个红色的“结束”圆圈。
    用户需在“开始”圆圈内按住鼠标左键，拖动光标至“结束”圆圈内并释放。拖动过程中，程序记录鼠标轨迹坐标 (x, y) 
    及各采样点之间的时间间隔。成功完成后，轨迹数据保存为 CSV 文件，并在控制台打印汇总统计信息（总用时、总距离、平均速度）。

创建日期：
    2025-07-15

依赖项：
    • Python 标准库：
        – random       （用于随机生成坐标）
        – time         （用于记录时间戳）
        – csv          （用于将轨迹写入 CSV）
        – hashlib      （用于生成唯一文件哈希）
        – datetime     （用于文件命名的时间戳）
    • 第三方库：
        – pygame       （用于图形界面和事件处理）

使用方法：
    1. 安装 pygame：`pip install pygame`
    2. 运行脚本：`python mouse_tracking_game.py`
    3. 按屏幕提示操作：
       • 在绿色圆圈内按住鼠标左键开始记录  
       • 按住左键拖动光标至红色圆圈  
       • 在红色圆圈内释放鼠标按钮以结束并保存数据  
       • 按 “R” 在开始前重新生成起止点  
       • 完成后按 “SPACE” 重置并重新开始  
       • 关闭窗口或点击关闭按钮退出游戏  

主要类与方法：
    class MouseTrackingGame:
        • __init__：初始化 Pygame 窗口、颜色、字体并生成起止点  
        • generate_points：随机定位开始/结束圆圈，并确保两者有最小距离  
        • is_point_near_target：检查给定 (x, y) 是否在目标圆圈半径范围内  
        • start_tracking：开始记录轨迹，保存起始时间和位置  
        • record_mouse_position：记录当前位置及两次采样的时间间隔  
        • finish_game：结束记录，保存终点位置，并调用 save_trajectory  
        • save_trajectory：将轨迹写入唯一命名的 CSV 文件，并打印统计信息  
        • draw：绘制游戏元素，包括圆圈和鼠标轨迹  
        • fail_and_reset：若在结束圆圈外释放鼠标，则重置游戏且不保存数据  
        • reset_game：重置游戏状态并重新生成起止点  
        • run：主循环，处理 Pygame 事件并更新/重绘画面  

数据输出：
    • CSV 文件名格式：X{start_x}Y{start_y}_X{end_x}Y{end_y}_{hash}.csv  
      其中 {hash} 为基于时间戳和轨迹长度生成的 8 字符 MD5 摘要  
    • CSV 列：x_coordinate, y_coordinate, time_interval_seconds  
    • 控制台输出：文件路径、样本数量、总用时（秒）、总距离（像素）、平均速度（像素/秒）  

注意事项：
    • 确保“开始”和“结束”圆圈之间有足够的距离，以获得有意义的轨迹  
    • 时间间隔以相邻两次记录的样本时间差计算  
    • 若用户在错误位置释放鼠标，则视为失败并自动重置，无数据保存  

"""

import random
import time
import csv
import hashlib
from datetime import datetime

class MouseTrackingGame:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Set window size
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Mouse Trajectory Tracking Game")
        
        # Color definitions
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GRAY = (128, 128, 128)
        
        # Game state
        self.game_started = False
        self.game_finished = False
        self.tracking = False
        
        # Trajectory data
        self.trajectory = []
        self.start_time = None
        self.last_time = None
        self.actual_start_pos = None
        self.actual_end_pos = None
        self.mouse_pressed = False
        
        # Start and end points
        self.start_point = None
        self.end_point = None
        self.point_radius = 15
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.generate_points()
    
    def generate_points(self):
        """Randomly generate start and end points"""
        margin = 50
        self.start_point = (
            random.randint(margin, self.width - margin),
            random.randint(margin, self.height - margin)
        )
        
        # Ensure end point is far enough from start point
        while True:
            self.end_point = (
                random.randint(margin, self.width - margin),
                random.randint(margin, self.height - margin)
            )
            distance = ((self.end_point[0] - self.start_point[0])**2 + 
                       (self.end_point[1] - self.start_point[1])**2)**0.5
            if distance > 200:  # Minimum distance 200 pixels
                break
    
    def is_point_near_target(self, pos, target, radius=20):
        """Check if point is near target"""
        distance = ((pos[0] - target[0])**2 + (pos[1] - target[1])**2)**0.5
        return distance <= radius
    
    def start_tracking(self, start_pos):
        """Start trajectory tracking"""
        self.tracking = True
        self.game_started = True
        self.mouse_pressed = True
        self.actual_start_pos = start_pos
        self.start_time = time.time()
        self.last_time = self.start_time
        self.trajectory = []
    
    def record_mouse_position(self, pos):
        """Record mouse position and time"""
        if self.tracking and self.mouse_pressed:
            current_time = time.time()
            time_diff = current_time - self.last_time
            
            self.trajectory.append({
                'x': pos[0],
                'y': pos[1],
                'time_diff': time_diff
            })
            
            self.last_time = current_time
    
    def finish_game(self, end_pos):
        """Finish game and save data"""
        self.tracking = False
        self.mouse_pressed = False
        self.game_finished = True
        self.actual_end_pos = end_pos
        self.save_trajectory()
    
    def save_trajectory(self):
        """Save trajectory data to CSV file"""
        if not self.trajectory or not self.actual_start_pos or not self.actual_end_pos:
            return
        
        # Generate filename using actual click positions
        start_x = round(self.actual_start_pos[0], 1)
        start_y = round(self.actual_start_pos[1], 1)
        end_x = round(self.actual_end_pos[0], 1)
        end_y = round(self.actual_end_pos[1], 1)
        
        # Generate hash code (based on timestamp and trajectory data)
        hash_data = f"{datetime.now().isoformat()}{len(self.trajectory)}{start_x}{start_y}{end_x}{end_y}"
        hash_code = hashlib.md5(hash_data.encode()).hexdigest()[:8]
        
        filename = f"../csv_data/X{start_x}Y{start_y}_X{end_x}Y{end_y}_{hash_code}.csv"
        
        # Save CSV file
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['x_coordinate', 'y_coordinate', 'time_interval_seconds'])
                
                for point in self.trajectory:
                    writer.writerow([point['x'], point['y'], round(point['time_diff'], 4)])
            
            print(f"Trajectory data saved to: {filename}")
            print(f"Total recorded trajectory points: {len(self.trajectory)}")
            
            # Calculate statistics
            total_time = sum(point['time_diff'] for point in self.trajectory)
            total_distance = 0
            for i in range(1, len(self.trajectory)):
                dx = self.trajectory[i]['x'] - self.trajectory[i-1]['x']
                dy = self.trajectory[i]['y'] - self.trajectory[i-1]['y']
                total_distance += (dx**2 + dy**2)**0.5
            
            avg_speed = total_distance / total_time if total_time > 0 else 0
            print(f"Total time: {total_time:.2f} seconds")
            print(f"Total distance: {total_distance:.1f} pixels")
            print(f"Average speed: {avg_speed:.1f} pixels/second")
            
        except Exception as e:
            print(f"Error saving file: {e}")
    
    def draw(self):
        """Draw game interface"""
        self.screen.fill(self.WHITE)
        
        if not self.game_started:
            # Draw start interface
            title_text = self.font.render("Mouse Trajectory Tracking Game", True, self.BLACK)
            title_rect = title_text.get_rect(center=(self.width//2, 100))
            self.screen.blit(title_text, title_rect)
            
            instruction_lines = [
                "Game Rules:",
                "1. Click and hold left mouse button inside green start circle",
                "2. While holding, move mouse to red end circle",
                "3. Release mouse button inside red end circle",
                "4. Game will record your mouse trajectory and timing",
                "5. Data will be saved automatically when successful",
                "",
                "Press R to regenerate start and end points"
            ]
            
            for i, line in enumerate(instruction_lines):
                text = self.small_font.render(line, True, self.BLACK)
                text_rect = text.get_rect(center=(self.width//2, 200 + i * 30))
                self.screen.blit(text, text_rect)
        
        # Draw start and end points
        if self.start_point:
            pygame.draw.circle(self.screen, self.GREEN, self.start_point, self.point_radius)
            start_text = self.small_font.render("START", True, self.BLACK)
            start_rect = start_text.get_rect(center=(self.start_point[0], self.start_point[1] - 30))
            self.screen.blit(start_text, start_rect)
        
        if self.end_point:
            pygame.draw.circle(self.screen, self.RED, self.end_point, self.point_radius)
            end_text = self.small_font.render("END", True, self.BLACK)
            end_rect = end_text.get_rect(center=(self.end_point[0], self.end_point[1] - 30))
            self.screen.blit(end_text, end_rect)
        
        # Draw trajectory
        if self.tracking and len(self.trajectory) > 1:
            points = [(point['x'], point['y']) for point in self.trajectory]
            if len(points) > 1:
                pygame.draw.lines(self.screen, self.BLUE, False, points, 2)
        
        # Draw current status information
        if self.tracking and self.mouse_pressed:
            status_text = self.small_font.render("Recording trajectory... Hold and move to red end circle", True, self.BLACK)
            self.screen.blit(status_text, (10, 10))
            
            # Show current number of recorded points
            points_text = self.small_font.render(f"Trajectory points: {len(self.trajectory)}", True, self.BLACK)
            self.screen.blit(points_text, (10, 35))
        
        if self.game_finished:
            finish_text = self.font.render("Game Complete! Data Saved", True, self.GREEN)
            finish_rect = finish_text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(finish_text, finish_rect)
            
            restart_text = self.small_font.render("Press SPACE to start new game", True, self.BLACK)
            restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 40))
            self.screen.blit(restart_text, restart_rect)
    
    def fail_and_reset(self):
        """Reset game due to failure"""
        self.tracking = False
        self.mouse_pressed = False
        self.game_started = False
        self.game_finished = False
        self.trajectory = []
        self.start_time = None
        self.last_time = None
        self.actual_start_pos = None
        self.actual_end_pos = None
        print("Failed! Mouse not in correct area. Try again!")
    
    def reset_game(self):
        """Reset game"""
        self.game_started = False
        self.game_finished = False
        self.tracking = False
        self.mouse_pressed = False
        self.trajectory = []
        self.start_time = None
        self.last_time = None
        self.actual_start_pos = None
        self.actual_end_pos = None
        self.generate_points()
    
    def run(self):
        """Run game main loop"""
        clock = pygame.time.Clock()
        running = True
        
        print("Game started!")
        print("Click and hold left mouse button inside green start circle to begin")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and not self.tracking:
                        # Regenerate points
                        self.generate_points()
                        print("Regenerated start and end points")
                    
                    elif event.key == pygame.K_SPACE and self.game_finished:
                        # Start new game
                        self.reset_game()
                        print("New game started!")
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Check if clicking inside start circle
                        if not self.game_started and self.is_point_near_target(mouse_pos, self.start_point, self.point_radius):
                            self.start_tracking(mouse_pos)
                            print("Started recording trajectory!")
                        elif not self.game_started:
                            print("Click inside the green start circle!")
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.tracking and self.mouse_pressed:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Check if releasing inside end circle
                        if self.is_point_near_target(mouse_pos, self.end_point, self.point_radius):
                            self.finish_game(mouse_pos)
                            print("Reached end point! Game complete!")
                        else:
                            self.fail_and_reset()
                
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Record mouse position only when tracking
                    self.record_mouse_position(mouse_pos)
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()

if __name__ == "__main__":
    # Check if pygame is installed
    try:
        import pygame
    except ImportError:
        print("Please install pygame library first: pip install pygame")
        exit(1)
    
    game = MouseTrackingGame()
    game.run()