"""
Vibrant Sparkle Fairy - Maximum Visual Effects
"""

import tkinter as tk
import math
import time
import random


class VibrantSparkleFairy:
    def __init__(self):
        # Create a transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("Vibrant Sparkle Fairy")
        
        # Set transparency and attributes
        self.root.configure(bg='white')
        self.root.attributes('-transparentcolor', 'white')  # Make white transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations
        
        # Size the window appropriately for the fairy
        self.root.geometry("200x200")
        
        # Position fairy in center of screen for visibility
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width // 2 - 100
        self.y = screen_height // 2 - 100
        self.root.geometry(f"200x200+{self.x}+{self.y}")
        
        # Create canvas for drawing the fairy
        self.canvas = tk.Canvas(
            self.root,
            width=200,
            height=200,
            bg='white',  # This will be transparent
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Fairy properties - larger and more vibrant
        self.orb_radius = 35
        self.eye_size = 8
        self.mouth_width = 7
        self.mouth_height = 4
        
        # Vibrant color palette
        self.orb_color = '#F8F8FF'  # More vibrant white-blue
        self.eye_color = '#6A5ACD'  # More vibrant slate blue
        self.mouth_color = '#BA55D3'  # More vibrant medium orchid
        self.wing_color = '#F0E6FF'  # More vibrant lavender
        
        # Animation properties
        self.blink_state = True
        self.blink_timer = 0
        self.wing_phase = 0
        self.bounce_offset = 0
        self.pulse_phase = 0
        
        # Maximum sparkle properties
        self.sparkles = []  # [(x, y, age, type, color, size), ...]
        self.ring_sparkles = []  # [(angle, distance, age, color), ...]
        self.trail_sparkles = []  # [(x, y, age, size), ...]
        
        # Draw initial fairy
        self.draw_fairy()
        
        # Start animation
        self.animate()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
    
    def draw_fairy(self):
        """Draw the fairy with maximum visual effects"""
        self.canvas.delete("all")
        
        # Calculate position for drawing
        draw_x, draw_y = 100, 100 + self.bounce_offset
        
        # Draw ring of sparkles around fairy
        for angle, distance, age, color in self.ring_sparkles[:]:
            ring_x = draw_x + distance * math.cos(angle)
            ring_y = draw_y + distance * math.sin(angle)
            
            # Update age
            idx = self.ring_sparkles.index((angle, distance, age, color))
            self.ring_sparkles[idx] = (angle, distance + 0.5, age + 1, color)
            
            # Remove old ring sparkles
            if age > 40:  # Remove after 1.3 seconds (30fps * 1.3)
                self.ring_sparkles.pop(idx)
                continue
                
            # Draw ring sparkle
            self.canvas.create_text(
                ring_x, ring_y, text="★", fill=color, font=("Arial", 8, "bold")
            )
        
        # Draw trail sparkles
        for i, (tx, ty, age, size) in enumerate(self.trail_sparkles[:]):
            if age < 25:  # Only draw for first half of life
                alpha = max(0, 255 - (age * 255 // 25))
                color_intensity = 180 + (75 * (25-age) // 25)
                color = f"#{color_intensity:02x}{color_intensity:02x}{255:02x}"  # Light blue
                self.canvas.create_oval(
                    tx - size, ty - size, tx + size, ty + size,
                    fill=color, outline="", stipple=""
                )
        
        # Draw background sparkles
        for i, (sx, sy, age, s_type, color, size) in enumerate(self.sparkles[:]):
            # Update age
            self.sparkles[i] = (sx, sy, age + 1, s_type, color, size)
            
            # Remove old sparkles
            if age > 50:  # Remove after ~1.7 seconds
                self.sparkles.pop(i)
                continue
            
            # Draw sparkle based on type
            if s_type == "star":
                self.canvas.create_text(
                    sx, sy, text="★", fill=color, font=("Arial", size, "bold")
                )
            elif s_type == "heart":
                self.canvas.create_text(
                    sx, sy, text="♥", fill=color, font=("Arial", size, "bold")
                )
            elif s_type == "circle":
                self.canvas.create_oval(
                    sx - size//2, sy - size//2, sx + size//2, sy + size//2,
                    fill=color, outline=""
                )
            elif s_type == "diamond":
                self.canvas.create_text(
                    sx, sy, text="◆", fill=color, font=("Arial", size, "bold")
                )
            elif s_type == "plus":
                self.canvas.create_text(
                    sx, sy, text="+", fill=color, font=("Arial", size, "bold")
                )
        
        # Draw pulsing aura around the fairy
        pulse_size = self.orb_radius + 8 + int(6 * math.sin(self.pulse_phase))
        self.canvas.create_oval(
            draw_x - pulse_size, 
            draw_y - pulse_size, 
            draw_x + pulse_size, 
            draw_y + pulse_size,
            outline='#9370DB', width=2, stipple='gray25'
        )
        
        # Draw the orb body with gradient effect
        for i in range(3):
            radius = self.orb_radius - i
            opacity = 200 - (i * 50)
            color_val = f"#{240-i*10:02x}{240-i*10:02x}{255-i*10:02x}"
            self.canvas.create_oval(
                draw_x - radius, 
                draw_y - radius, 
                draw_x + radius, 
                draw_y + radius,
                fill=color_val, outline='#D8BFD8', width=1
            )
        
        # Draw subtle texture on orb
        for i in range(12):
            angle = (i * 30) * math.pi / 180
            x = draw_x + (self.orb_radius - 8) * math.cos(angle)
            y = draw_y + (self.orb_radius - 8) * math.sin(angle)
            size = random.randint(1, 3)
            self.canvas.create_oval(x-size, y-size, x+size, y+size, fill='#E6E6FA', outline='')
        
        # Draw cheeks
        self.canvas.create_oval(
            draw_x - 18, draw_y + 5,
            draw_x - 10, draw_y + 12,
            fill='#FFB6C1', outline='', stipple=''
        )
        self.canvas.create_oval(
            draw_x + 10, draw_y + 5,
            draw_x + 18, draw_y + 12,
            fill='#FFB6C1', outline='', stipple=''
        )
        
        # Draw eyes
        left_eye_x = draw_x - 14
        right_eye_x = draw_x + 14
        eye_y = draw_y - 6
        
        if self.blink_state:
            # Draw open eyes with highlights
            self.canvas.create_oval(
                left_eye_x - self.eye_size, eye_y - self.eye_size,
                left_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#D0D0D0', width=2
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size, eye_y - self.eye_size,
                right_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#D0D0D0', width=2
            )
            
            # Draw irises with shine
            iris_size = self.eye_size * 0.7
            self.canvas.create_oval(
                left_eye_x - iris_size, eye_y - iris_size,
                left_eye_x + iris_size, eye_y + iris_size,
                fill=self.eye_color, outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - iris_size, eye_y - iris_size,
                right_eye_x + iris_size, eye_y + iris_size,
                fill=self.eye_color, outline='', width=1
            )
            
            # Draw pupils with shine
            pupil_size = 3
            self.canvas.create_oval(
                left_eye_x - pupil_size, eye_y - pupil_size,
                left_eye_x + pupil_size, eye_y + pupil_size,
                fill='#2F2F2F', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - pupil_size, eye_y - pupil_size,
                right_eye_x + pupil_size, eye_y + pupil_size,
                fill='#2F2F2F', outline='', width=1
            )
            
            # Draw eye highlights
            self.canvas.create_oval(
                left_eye_x - 1, eye_y - 2,
                left_eye_x + 0.5, eye_y - 0.5,
                fill='#FFFFFF', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 1, eye_y - 2,
                right_eye_x + 0.5, eye_y - 0.5,
                fill='#FFFFFF', outline='', width=1
            )
        else:
            # Draw closed eyes
            self.canvas.create_arc(
                left_eye_x - self.eye_size, eye_y - 1,
                left_eye_x + self.eye_size, eye_y + 1,
                start=0, extent=-180, style=tk.ARC, 
                outline='#2F2F2F', width=2
            )
            self.canvas.create_arc(
                right_eye_x - self.eye_size, eye_y - 1,
                right_eye_x + self.eye_size, eye_y + 1,
                start=0, extent=-180, style=tk.ARC, 
                outline='#2F2F2F', width=2
            )
        
        # Draw mouth with more expression
        mouth_y = draw_y + 16
        self.canvas.create_arc(
            draw_x - self.mouth_width//2, 
            mouth_y - self.mouth_height//4,
            draw_x + self.mouth_width//2, 
            mouth_y + self.mouth_height//4,
            start=10, extent=-160, style=tk.ARC, 
            fill='', outline=self.mouth_color, width=2
        )
        
        # Draw wings with more detail
        wing_offset = math.sin(self.wing_phase) * 5
        
        # Left wing with gradient
        left_wing_points = [
            draw_x - 45, draw_y - 15 + wing_offset,
            draw_x - 55, draw_y - 25,
            draw_x - 47, draw_y + 3,
            draw_x - 37, draw_y - 7
        ]
        self.canvas.create_polygon(
            left_wing_points, fill=self.wing_color, outline='#D8BFD8', width=2
        )
        
        # Right wing with gradient
        right_wing_points = [
            draw_x + 45, draw_y - 15 - wing_offset,
            draw_x + 55, draw_y - 25,
            draw_x + 47, draw_y + 3,
            draw_x + 37, draw_y - 7
        ]
        self.canvas.create_polygon(
            right_wing_points, fill=self.wing_color, outline='#D8BFD8', width=2
        )
        
        # Add wing details
        self.canvas.create_line(
            draw_x - 45, draw_y - 10 + wing_offset,
            draw_x - 47, draw_y,
            fill='#D8BFD8', width=1
        )
        self.canvas.create_line(
            draw_x + 45, draw_y - 10 - wing_offset,
            draw_x + 47, draw_y,
            fill='#D8BFD8', width=1
        )
    
    def animate(self):
        """Vibrant animation with maximum visual effects"""
        # Handle blinking
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            if random.randint(0, 90) == 0:  # Less frequent blinking
                self.blink_state = False
                self.blink_timer = 15
        
        # Wing animation
        self.wing_phase += 0.2  # Faster wing movement
        
        # Bounce animation
        self.bounce_offset = math.sin(time.time() * 2.5) * 2  # Slightly faster bounce
        
        # Pulse animation
        self.pulse_phase += 0.15
        
        # Add lots of sparkles at high frequency
        if random.randint(0, 3) == 0:  # Very frequent sparkles
            # Position sparkles around the fairy
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(25, 80)
            sparkle_x = 100 + distance * math.cos(angle)
            sparkle_y = 100 + self.bounce_offset + distance * math.sin(angle)
            
            # Random sparkle type
            sparkle_types = ["star", "heart", "circle", "diamond", "plus"]
            s_type = random.choice(sparkle_types)
            
            # Vibrant colors
            colors = ["#FFD700", "#FF69B4", "#9370DB", "#32CD32", "#4169E1", "#FF4500", "#BA55D3"]
            color = random.choice(colors)
            
            # Random size
            size = random.randint(8, 14)
            
            self.sparkles.append((sparkle_x, sparkle_y, 0, s_type, color, size))
        
        # Add ring sparkles
        if random.randint(0, 8) == 0:  # Add ring sparkles periodically
            angle = random.uniform(0, 2 * math.pi)
            distance = 50  # Starting distance
            colors = ["#FFD700", "#FF69B4", "#9370DB", "#32CD32", "#FF4500"]
            color = random.choice(colors)
            self.ring_sparkles.append((angle, distance, 0, color))
        
        # Add trail sparkles
        if random.randint(0, 4) == 0:  # Add trail sparkles frequently
            trail_x = 100 + random.randint(-30, 30)
            trail_y = 100 + self.bounce_offset + random.randint(-30, 30)
            size = random.randint(2, 4)
            self.trail_sparkles.append((trail_x, trail_y, 0, size))
        
        # Update trail sparkles
        for i in range(len(self.trail_sparkles)):
            x, y, age, size = self.trail_sparkles[i]
            self.trail_sparkles[i] = (x, y, age + 1, size)
        
        # Remove old trail sparkles
        self.trail_sparkles = [p for p in self.trail_sparkles if p[2] < 25]
        
        # Simple position maintenance (no orbit for now)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Keep in center but allow slight movement
        center_x = screen_width // 2 - 100
        center_y = screen_height // 2 - 100
        
        # Update position to stay centered
        self.x = center_x
        self.y = center_y
        self.root.geometry(f"200x200+{int(self.x)}+{int(self.y)}")
        
        # Redraw fairy
        self.draw_fairy()
        
        # Schedule next animation frame
        self.root.after(30, self.animate)
    
    def on_drag_start(self, event):
        """Begin dragging the fairy"""
        self.drag_data = {"x": event.x, "y": event.y, "start_x": self.x, "start_y": self.y}
    
    def on_drag(self, event):
        """Handle dragging the fairy"""
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        new_x = self.drag_data["start_x"] + dx
        new_y = self.drag_data["start_y"] + dy
        
        self.x = new_x
        self.y = new_y
        self.root.geometry(f"200x200+{self.x}+{self.y}")
    
    def on_drag_stop(self, event):
        """Stop dragging the fairy"""
        pass
    
    def run(self):
        """Start the fairy system"""
        self.root.mainloop()


def main():
    print("Starting Vibrant Sparkle Fairy...")
    print("Features:")
    print("- Maximum sparkle density")
    print("- Ring of sparkles around fairy")
    print("- Pulsing magical aura")
    print("- Trail sparkles following movement")
    print("- Vibrant colors and enhanced visual effects")
    print("- Larger, more detailed fairy design")
    
    fairy = VibrantSparkleFairy()
    fairy.run()


if __name__ == "__main__":
    main()