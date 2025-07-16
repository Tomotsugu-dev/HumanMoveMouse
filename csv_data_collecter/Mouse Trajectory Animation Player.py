import csv
import time
import os
import math

# Import pygame at the top level
try:
    import pygame
except ImportError:
    print("Error: The 'pygame' library is not installed.")
    print("Please install it by running: pip install pygame")
    exit(1)

class TrajectoryPlayer:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Increase window size
        self.width = 1600
        self.height = 1000
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Mouse Trajectory Animation Player")
        
        # Color definitions - using a more modern color scheme
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (39, 174, 96)
        self.RED = (231, 76, 60)
        self.BLUE = (52, 152, 219)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (220, 220, 220) # Made this lighter for the background path
        self.YELLOW = (241, 196, 15)
        self.ORANGE = (230, 126, 34)
        self.DARK_GRAY = (44, 62, 80)
        self.PURPLE = (155, 89, 182)
        self.TURQUOISE = (26, 188, 156)
        self.PANEL_BG = (255, 255, 255, 230) # Translucent white
        
        # Animation state
        self.playing = False
        self.paused = False
        self.current_point_index = 0
        self.animation_start_time = None
        self.pause_time = 0
        self.total_pause_time = 0
        
        # Speed settings
        self.speed_options = [0.25, 0.5, 1.0, 2.0, 4.0]
        self.current_speed_index = 2 # Start with 1x speed
        self.current_speed = self.speed_options[self.current_speed_index]
        
        # Trajectory data
        self.trajectory_data = []
        self.file_loaded = False
        self.csv_filename = ""
        
        # Animation trail
        self.trail_points = []
        self.max_trail_length = 100 # A shorter, fading trail looks good against the full path
        
        # Fonts
        try:
            font_path = r"calibri.ttf"
            self.font = pygame.font.Font(font_path, 36)
            self.small_font = pygame.font.Font(font_path, 24)
            self.large_font = pygame.font.Font(font_path, 56)
            self.tiny_font = pygame.font.Font(font_path, 20)
        except:
            self.font = pygame.font.SysFont('Arial', 36)
            self.small_font = pygame.font.SysFont('Arial', 24)
            self.large_font = pygame.font.SysFont('Arial', 56)
            self.tiny_font = pygame.font.SysFont('Arial', 20)
        
        # File selection
        self.file_list = []
        self.selected_file_index = 0
        self.file_selection_active = True
        self.scan_csv_files()
        
        # Trajectory display area
        self.track_offset_x = (self.width - 1200) // 2
        self.track_offset_y = (self.height - 800) // 2

    def scan_csv_files(self):
        """Scan 'csv_data' subdirectory for CSV files"""
        try:
            # MODIFIED: Look inside the 'csv_data' subdirectory
            csv_dir = '../csv_data'
            if not os.path.isdir(csv_dir):
                self.file_list = [f"Error: Folder '{csv_dir}' not found."]
                self.selected_file_index = 0
                print(f"Error: Subdirectory '{csv_dir}' not found.")
                return

            files_in_dir = [f for f in os.listdir(csv_dir) if f.lower().endswith('.csv')]
            # Store the full relative path for each file
            self.file_list = sorted([os.path.join(csv_dir, f) for f in files_in_dir])
            
            if not self.file_list:
                self.file_list = [f"No CSV files found in '{csv_dir}'"]
            
            self.selected_file_index = min(self.selected_file_index, len(self.file_list) - 1)
            self.selected_file_index = max(0, self.selected_file_index)
            print(f"Found {len([f for f in self.file_list if f.endswith('.csv')])} CSV files in '{csv_dir}'")

        except Exception as e:
            print(f"Error scanning directory: {e}")
            self.file_list = ["Error scanning directory"]
            self.selected_file_index = 0

    def load_csv_file(self, filename):
        """Load trajectory data from CSV and pre-calculate timestamps"""
        try:
            self.trajectory_data = []
            cumulative_time = 0.0
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                _ = next(reader) # Skip header
                
                for row in reader:
                    if len(row) >= 3:
                        x = float(row[0])
                        y = float(row[1])
                        time_interval = float(row[2])
                        # MODIFICATION: Pre-calculate cumulative timestamps for easy lookup
                        cumulative_time += time_interval
                        self.trajectory_data.append({
                            'x': x,
                            'y': y,
                            'time_interval': time_interval,
                            'timestamp': cumulative_time # Add cumulative time
                        })
            
            self.file_loaded = True
            self.csv_filename = filename
            self.reset_animation()
            print(f"Loaded {len(self.trajectory_data)} trajectory points from {filename}")
            return True
            
        except Exception as e:
            print(f"Error loading file {filename}: {e}")
            self.file_loaded = False
            return False

    def reset_animation(self):
        """Reset animation to beginning"""
        self.playing = False
        self.paused = False
        self.current_point_index = 0
        self.animation_start_time = None
        self.pause_time = 0
        self.total_pause_time = 0
        self.trail_points = []

    def start_animation(self):
        """Start or resume animation"""
        if not self.file_loaded:
            return
            
        if self.paused:
            self.total_pause_time += time.time() - self.pause_time
            self.paused = False
        else:
            self.animation_start_time = time.time()
            self.total_pause_time = 0
            self.current_point_index = 0
            self.trail_points = []
        
        self.playing = True

    def pause_animation(self):
        """Pause animation"""
        if self.playing and not self.paused:
            self.paused = True
            self.pause_time = time.time()
            self.playing = False

    def change_speed(self, direction):
        """Change playback speed and adjust timing to maintain progress"""
        old_speed = self.current_speed
        
        if direction > 0:
            self.current_speed_index = min(len(self.speed_options) - 1, self.current_speed_index + 1)
        else:
            self.current_speed_index = max(0, self.current_speed_index - 1)
        
        self.current_speed = self.speed_options[self.current_speed_index]
        
        if self.playing and old_speed != self.current_speed:
            current_time = time.time()
            elapsed_real_time = current_time - self.animation_start_time - self.total_pause_time
            elapsed_animation_time = elapsed_real_time * old_speed
            
            # Recalculate start time based on new speed to keep animation at the same spot
            self.animation_start_time = current_time - (elapsed_animation_time / self.current_speed)

    def get_current_animation_time(self):
        """Calculates the elapsed animation time, factoring in speed and pauses."""
        if not self.animation_start_time:
            return 0
        
        current_time = time.time()
        pause_duration = self.total_pause_time
        if self.paused:
            # Add current pause duration if paused right now
            pause_duration += current_time - self.pause_time

        elapsed_real_time = current_time - self.animation_start_time - pause_duration
        return elapsed_real_time * self.current_speed

    def update_animation(self):
        """Update animation state by finding the current point index."""
        if not self.playing or not self.file_loaded:
            return
        
        elapsed_animation_time = self.get_current_animation_time()
        
        # Find which point index we should be at
        target_index = self.current_point_index
        for i in range(self.current_point_index, len(self.trajectory_data)):
            if self.trajectory_data[i]['timestamp'] >= elapsed_animation_time:
                target_index = i
                break
        else:
            # If loop finishes, we are at the end
            target_index = len(self.trajectory_data) - 1
            self.playing = False # Animation finished
        
        # Add intermediate points to the trail to avoid gaps at high speeds
        if target_index > self.current_point_index:
            for i in range(self.current_point_index, target_index + 1):
                point = self.trajectory_data[i]
                self.trail_points.append((point['x'] + self.track_offset_x, 
                                          point['y'] + self.track_offset_y))
                if len(self.trail_points) > self.max_trail_length:
                    self.trail_points.pop(0)

        self.current_point_index = target_index

    def draw_file_selection(self):
        """Draw file selection interface"""
        # Gradient background
        for y in range(self.height):
            color_value = int(255 - (y / self.height) * 30)
            pygame.draw.line(self.screen, (color_value, color_value, color_value), (0, y), (self.width, y))
        
        # Title and instructions
        title_text = self.large_font.render("Mouse Trajectory Player", True, self.DARK_GRAY)
        self.screen.blit(title_text, title_text.get_rect(center=(self.width//2, 80)))
        subtitle_text = self.font.render("Select a CSV file to play", True, self.DARK_GRAY)
        self.screen.blit(subtitle_text, subtitle_text.get_rect(center=(self.width//2, 140)))
        
        # File list box
        list_bg = pygame.Rect(self.width//2 - 500, 220, 1000, 600)
        pygame.draw.rect(self.screen, self.WHITE, list_bg, border_radius=10)
        pygame.draw.rect(self.screen, self.DARK_GRAY, list_bg, 2, border_radius=10)
        
        # File list items
        if self.file_list:
            list_start_y, visible_files = 240, 18
            start_index = max(0, self.selected_file_index - visible_files // 2)
            end_index = min(len(self.file_list), start_index + visible_files)
            
            for i in range(start_index, end_index):
                # MODIFIED: Get just the filename for display, not the full path
                display_name = os.path.basename(self.file_list[i])
                y_pos = list_start_y + (i - start_index) * 32
                
                if i == self.selected_file_index:
                    highlight_rect = pygame.Rect(self.width//2 - 480, y_pos - 5, 960, 30)
                    pygame.draw.rect(self.screen, self.BLUE, highlight_rect, border_radius=5)
                    text_color = self.WHITE
                else:
                    text_color = self.DARK_GRAY
                
                file_text = self.small_font.render(display_name, True, text_color)
                self.screen.blit(file_text, file_text.get_rect(midleft=(self.width//2 - 470, y_pos + 10)))
        
        # Controls help text
        controls_bg = pygame.Rect(self.width//2 - 500, 840, 1000, 100)
        pygame.draw.rect(self.screen, (245, 245, 245), controls_bg, border_radius=10)
        controls_text = self.small_font.render("↑↓ - Select | ENTER - Load | R - Refresh | ESC - Exit", True, self.DARK_GRAY)
        self.screen.blit(controls_text, controls_text.get_rect(center=(self.width//2, 890)))

    def draw_animation(self):
        """Draw animation interface"""
        self.screen.fill((248, 248, 248))
        
        if not self.file_loaded or not self.trajectory_data:
            return
        
        track_border = pygame.Rect(self.track_offset_x - 2, self.track_offset_y - 2, 1204, 804)
        pygame.draw.rect(self.screen, self.GRAY, track_border, 2, border_radius=5)
        
        # MODIFICATION: Draw the complete trajectory path in the background
        if len(self.trajectory_data) > 1:
            full_path_points = [(p['x'] + self.track_offset_x, p['y'] + self.track_offset_y) for p in self.trajectory_data]
            pygame.draw.lines(self.screen, self.LIGHT_GRAY, False, full_path_points, 2)

        # Draw the fading trail
        if len(self.trail_points) > 1:
            for i in range(1, len(self.trail_points)):
                alpha = i / len(self.trail_points)
                color = (
                    int(self.PURPLE[0] * (1-alpha) + self.TURQUOISE[0] * alpha),
                    int(self.PURPLE[1] * (1-alpha) + self.TURQUOISE[1] * alpha),
                    int(self.PURPLE[2] * (1-alpha) + self.TURQUOISE[2] * alpha)
                )
                pygame.draw.line(self.screen, color, self.trail_points[i-1], self.trail_points[i], max(1, int(4 * alpha)))

        # Draw current position with interpolation for smoothness
        current_x, current_y = 0, 0
        if self.playing:
            # MODIFICATION: Interpolate current position for smooth playback
            elapsed_time = self.get_current_animation_time()
            p_prev = self.trajectory_data[self.current_point_index - 1] if self.current_point_index > 0 else self.trajectory_data[0]
            p_next = self.trajectory_data[self.current_point_index]

            segment_duration = p_next['timestamp'] - p_prev['timestamp']
            time_into_segment = elapsed_time - p_prev['timestamp']
            
            t = time_into_segment / segment_duration if segment_duration > 0 else 1.0
            t = max(0.0, min(1.0, t)) # Clamp t between 0 and 1

            current_x = p_prev['x'] + t * (p_next['x'] - p_prev['x'])
            current_y = p_prev['y'] + t * (p_next['y'] - p_prev['y'])
        else:
            # When paused or stopped, snap to the exact point
            pos = self.trajectory_data[self.current_point_index]
            current_x, current_y = pos['x'], pos['y']

        x = current_x + self.track_offset_x
        y = current_y + self.track_offset_y
        
        # Pulsing outer circle for the cursor
        animation_radius = 12 + 3 * math.sin(time.time() * 5)
        pygame.draw.circle(self.screen, (*self.RED, 100), (int(x), int(y)), int(animation_radius), 2)
        pygame.draw.circle(self.screen, self.RED, (int(x), int(y)), 8)
        
        # Draw start and end points
        start_pos, end_pos = self.trajectory_data[0], self.trajectory_data[-1]
        start_x, start_y = start_pos['x'] + self.track_offset_x, start_pos['y'] + self.track_offset_y
        end_x, end_y = end_pos['x'] + self.track_offset_x, end_pos['y'] + self.track_offset_y
        
        pygame.draw.circle(self.screen, self.GREEN, (int(start_x), int(start_y)), 10)
        pygame.draw.circle(self.screen, self.WHITE, (int(start_x), int(start_y)), 6)
        pygame.draw.circle(self.screen, self.ORANGE, (int(end_x), int(end_y)), 10)
        pygame.draw.circle(self.screen, self.WHITE, (int(end_x), int(end_y)), 6)

        self.draw_top_panel()
        self.draw_bottom_controls()

    def draw_top_panel(self):
        """Draw top status panel"""
        panel_surface = pygame.Surface((self.width, 60), pygame.SRCALPHA)
        panel_surface.fill(self.PANEL_BG)
        self.screen.blit(panel_surface, (0, 0))
        pygame.draw.line(self.screen, self.GRAY, (0, 60), (self.width, 60), 1)

        # Info text
        file_text = f"File: {os.path.basename(self.csv_filename)}"
        self.screen.blit(self.small_font.render(file_text, True, self.DARK_GRAY), (20, 20))
        
        progress_text = f"Progress: {self.current_point_index + 1}/{len(self.trajectory_data)}"
        self.screen.blit(self.small_font.render(progress_text, True, self.DARK_GRAY), (640, 20))

        # Status indicator
        status, color = ("Playing", self.GREEN) if self.playing else (("Paused", self.ORANGE) if self.paused else ("Stopped", self.RED))
        self.screen.blit(self.small_font.render(status, True, color), (850, 20))
        
        # Speed indicator
        speed_text = f"Speed: {self.current_speed}x"
        rendered_speed = self.small_font.render(speed_text, True, self.WHITE)
        speed_bg_rect = pygame.Rect(0, 0, 150, 40)
        speed_bg_rect.center = (1125, 30)
        pygame.draw.rect(self.screen, self.BLUE, speed_bg_rect, border_radius=20)
        self.screen.blit(rendered_speed, rendered_speed.get_rect(center=speed_bg_rect.center))

    def draw_bottom_controls(self):
        """Draw bottom control bar"""
        panel_height = 80
        panel_surface = pygame.Surface((self.width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.PANEL_BG)
        self.screen.blit(panel_surface, (0, self.height - panel_height))
        pygame.draw.line(self.screen, self.GRAY, (0, self.height - panel_height), (self.width, self.height - panel_height), 1)

        # Progress bar
        if self.trajectory_data:
            progress = self.current_point_index / max(1, len(self.trajectory_data) - 1)
            bar_x, bar_y, bar_width, bar_height = 50, self.height - 50, self.width - 100, 20
            
            pygame.draw.rect(self.screen, self.LIGHT_GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=10)
            progress_width = int(bar_width * progress)
            pygame.draw.rect(self.screen, self.BLUE, (bar_x, bar_y, progress_width, bar_height), border_radius=10)
            pygame.draw.rect(self.screen, self.DARK_GRAY, (bar_x, bar_y, bar_width, bar_height), 1, border_radius=10)

        # Controls help text
        controls_text = "Space: Play/Pause  |  ↑↓: Speed  |  ←→: Switch File  |  ESC: Back"
        rendered_controls = self.tiny_font.render(controls_text, True, self.DARK_GRAY)
        self.screen.blit(rendered_controls, rendered_controls.get_rect(center=(self.width//2, self.height - 15)))

    def load_adjacent_file(self, direction):
        """Load the previous or next file in the list."""
        if not self.file_list or len(self.file_list) <= 1 or "Error" in self.file_list[0]:
            return
        
        # Find the index of the current file
        try:
            # MODIFIED: Find the index of the full path directly
            current_index = self.file_list.index(self.csv_filename)
        except ValueError:
            current_index = self.selected_file_index

        new_index = (current_index + direction) % len(self.file_list)
        
        if self.file_list[new_index].endswith('.csv'):
            self.selected_file_index = new_index
            if self.load_csv_file(self.file_list[new_index]):
                self.start_animation() # Automatically start playing the new file

    def handle_file_selection_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.file_list: self.selected_file_index = (self.selected_file_index - 1) % len(self.file_list)
            elif event.key == pygame.K_DOWN:
                if self.file_list: self.selected_file_index = (self.selected_file_index + 1) % len(self.file_list)
            elif event.key == pygame.K_RETURN:
                if self.file_list and self.file_list[self.selected_file_index].endswith('.csv'):
                    if self.load_csv_file(self.file_list[self.selected_file_index]):
                        self.file_selection_active = False
            elif event.key == pygame.K_r:
                self.scan_csv_files()
            elif event.key == pygame.K_ESCAPE:
                return False # Signal to exit program
        return True

    def handle_animation_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.playing: self.pause_animation()
                else: self.start_animation()
            elif event.key == pygame.K_UP:
                self.change_speed(1)
            elif event.key == pygame.K_DOWN:
                self.change_speed(-1)
            elif event.key == pygame.K_LEFT:
                self.load_adjacent_file(-1)
            elif event.key == pygame.K_RIGHT:
                self.load_adjacent_file(1)
            elif event.key == pygame.K_ESCAPE:
                self.file_selection_active = True
                self.file_loaded = False
                self.reset_animation()
                self.scan_csv_files()

    def run(self):
        """Main application loop."""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.file_selection_active:
                    if not self.handle_file_selection_events(event):
                        running = False
                else:
                    self.handle_animation_events(event)
            
            # Update game state
            if not self.file_selection_active:
                self.update_animation()
            
            # Draw everything
            if self.file_selection_active:
                self.draw_file_selection()
            else:
                self.draw_animation()
            
            pygame.display.flip()
            clock.tick(60) # Limit to 60 FPS
        
        pygame.quit()


if __name__ == "__main__":
    player = TrajectoryPlayer()
    player.run()