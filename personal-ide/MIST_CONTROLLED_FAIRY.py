"""
MIST-Controlled Fairy - Full Automation by MIST
"""

import tkinter as tk
import math
import time
import random
import threading
import queue


class MISTControlledFairy:
    def __init__(self):
        # Create a transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("MIST-Controlled Fairy")
        
        # Set transparency and attributes
        self.root.configure(bg='black')  # Changed to black for cosmic effect
        self.root.attributes('-transparentcolor', 'black')  # Make black transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations
        
        # Size the window appropriately for the detailed fairy
        self.root.geometry("220x220")
        
        # Position fairy in center of screen initially
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width // 2 - 110
        self.y = screen_height // 2 - 110
        self.root.geometry(f"220x220+{self.x}+{self.y}")
        
        # Create canvas for drawing the fairy
        self.canvas = tk.Canvas(
            self.root,
            width=220,
            height=220,
            bg='black',  # This will be transparent
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Fairy properties - detailed cosmic design
        self.body_radius = 40
        self.eye_size = 10
        self.mouth_width = 8
        self.mouth_height = 5
        
        # Cosmic/Mars color palette
        self.body_color = '#F8F0FF'  # Ethereal light purple-white
        self.eye_color = '#FF6B6B'  # Mars red for cosmic connection
        self.mouth_color = '#FF8E8E'  # Subtle mars-red
        self.wing_color = '#E6E6FA'  # Cosmic lavender
        self.wing_edge = '#FF6B6B'  # Mars red edges
        
        # Mars/cosmic elements
        self.mars_symbol = "♂"  # Mars symbol
        
        # Animation properties
        self.blink_state = True
        self.blink_timer = 0
        self.wing_phase = 0
        self.float_offset = 0
        self.pulse_phase = 0
        self.cosmic_phase = 0
        
        # Movement properties - controlled by MIST
        self.target_x = self.x + 110  # Center of fairy in screen coords
        self.target_y = self.y + 110  # Center of fairy in screen coords
        self.move_speed = 0.05  # Slower, smoother movement
        self.current_x = self.target_x
        self.current_y = self.target_y
        
        # Visual state properties
        self.visual_mode = "normal"  # "normal", "observing", "searching", "focused"
        self.state_timer = 0
        
        # Cosmic particle properties
        self.stars = []
        self.mars_particles = []
        self.cosmic_trails = []
        self.max_cosmic_elements = 60  # Limit for performance
        
        # Command queue for external control
        self.command_queue = queue.Queue()
        
        # Bind mouse events for dragging (MIST can still override)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
        
        # Draw initial fairy
        self.draw_fairy()
        
        # Start animation
        self.animate()
    
    def set_position(self, x, y):
        """Set target position for the fairy (called externally)"""
        self.target_x = x
        self.target_y = y
    
    def set_visual_mode(self, mode):
        """Set the visual mode of the fairy"""
        self.visual_mode = mode
        self.state_timer = 120  # Reset timer (4 seconds at 30fps)
    
    def process_commands(self):
        """Process commands from the queue"""
        try:
            while True:
                cmd = self.command_queue.get_nowait()
                if cmd[0] == "move":
                    self.set_position(cmd[1], cmd[2])
                elif cmd[0] == "mode":
                    self.set_visual_mode(cmd[1])
        except queue.Empty:
            pass
    
    def draw_fairy(self):
        """Draw the detailed cosmic fairy with Mars elements"""
        self.canvas.delete("all")
        
        # Calculate position for drawing (center of canvas)
        draw_x, draw_y = 110, 110 + self.float_offset
        
        # Draw cosmic background elements first
        # Draw distant stars
        for star_x, star_y, brightness, size in self.stars:
            self.canvas.create_oval(
                star_x - size, star_y - size,
                star_x + size, star_y + size,
                fill=f"#{brightness:02x}{brightness:02x}{brightness:02x}",
                outline=""
            )
        
        # Draw Mars-colored particles
        for mx, my, age, size in self.mars_particles:
            # Update age
            idx = self.mars_particles.index((mx, my, age, size))
            self.mars_particles[idx] = (mx, my, age + 1, size)
            
            # Remove old particles
            if age > 40:  # Remove after ~1.3 seconds
                self.mars_particles.pop(idx)
                continue
            
            # Draw Mars particle
            color_intensity = 255 - (age * 255 // 40)
            color = f"#{color_intensity:02x}{max(0, color_intensity-100):02x}{max(0, color_intensity-150):02x}"
            self.canvas.create_oval(
                mx - size//2, my - size//2,
                mx + size//2, my + size//2,
                fill=color, outline=""
            )
        
        # Draw cosmic trails
        for cx, cy, age, size in self.cosmic_trails:
            # Update age
            idx = self.cosmic_trails.index((cx, cy, age, size))
            self.cosmic_trails[idx] = (cx, cy, age + 1, size)
            
            # Remove old trails
            if age > 30:  # Remove after 1 second
                self.cosmic_trails.pop(idx)
                continue
            
            # Draw cosmic trail
            alpha = 255 - (age * 255 // 30)
            color = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
            self.canvas.create_oval(
                cx - size//2, cy - size//2,
                cx + size//2, cy + size//2,
                fill=color, outline=""
            )
        
        # Draw visual mode indicators
        if self.visual_mode == "observing":
            # Draw cosmic observing rings
            for i in range(3):
                ring_size = self.body_radius + 20 + i * 10 + int(5 * math.sin(self.pulse_phase + i))
                self.canvas.create_oval(
                    draw_x - ring_size, 
                    draw_y - ring_size, 
                    draw_x + ring_size, 
                    draw_y + ring_size,
                    outline='#4ECDC4', width=2, stipple='gray25'
                )
        elif self.visual_mode == "searching":
            # Draw cosmic searching spiral
            for i in range(12):
                angle = self.pulse_phase * 2 + i * math.pi / 6
                dist = 35 + i * 4
                x = draw_x + dist * math.cos(angle)
                y = draw_y + dist * math.sin(angle)
                self.canvas.create_text(
                    x, y, text="★", fill='#FFE66D', font=("Arial", 8)
                )
        elif self.visual_mode == "focused":
            # Draw cosmic focused beam
            self.canvas.create_line(
                draw_x, draw_y + self.body_radius,
                draw_x, 200,
                fill='#1A535C', width=4, stipple='gray50'
            )
        
        # Draw cosmic aura around the fairy
        aura_size = self.body_radius + 10 + int(8 * math.sin(self.pulse_phase))
        aura_color = '#A1C4FD'
        if self.visual_mode == "observing":
            aura_color = '#4ECDC4'
        elif self.visual_mode == "searching":
            aura_color = '#FFE66D'
        elif self.visual_mode == "focused":
            aura_color = '#1A535C'
        
        # Draw multiple layers for cosmic aura
        for i in range(3):
            layer_size = aura_size - i * 3
            self.canvas.create_oval(
                draw_x - layer_size, 
                draw_y - layer_size, 
                draw_x + layer_size, 
                draw_y + layer_size,
                outline=aura_color, width=2-i, stipple='gray25' if i > 0 else ''
            )
        
        # Draw the main ethereal body with gradient
        for i in range(5):
            radius = self.body_radius - i
            opacity = 200 - (i * 30)
            color_val = f"#{240-i*10:02x}{230-i*5:02x}{255-i*5:02x}"
            self.canvas.create_oval(
                draw_x - radius, 
                draw_y - radius, 
                draw_x + radius, 
                draw_y + radius,
                fill=color_val, outline='#D8BFD8', width=1
            )
        
        # Draw cosmic texture on body (small stars/dots)
        for i in range(15):
            angle = (i * 24) * math.pi / 180
            distance = self.body_radius - 10
            x = draw_x + distance * math.cos(angle)
            y = draw_y + distance * math.sin(angle)
            size = random.randint(1, 2)
            self.canvas.create_oval(
                x-size, y-size, x+size, y+size,
                fill='#E6E6FA', outline=''
            )
        
        # Draw cheeks with cosmic blush
        self.canvas.create_oval(
            draw_x - 22, draw_y + 8,
            draw_x - 12, draw_y + 18,
            fill='#FFB6C1', outline='', stipple=''
        )
        self.canvas.create_oval(
            draw_x + 12, draw_y + 8,
            draw_x + 22, draw_y + 18,
            fill='#FFB6C1', outline='', stipple=''
        )
        
        # Draw cosmic eyes with Mars symbolism
        left_eye_x = draw_x - 16
        right_eye_x = draw_x + 16
        eye_y = draw_y - 8
        
        if self.blink_state:
            # Draw open cosmic eyes with highlights
            self.canvas.create_oval(
                left_eye_x - self.eye_size, eye_y - self.eye_size,
                left_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#FFB6C1', width=2
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size, eye_y - self.eye_size,
                right_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#FFB6C1', width=2
            )
            
            # Draw Mars-red irises
            iris_size = self.eye_size * 0.8
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
            
            # Draw pupils with cosmic detail
            pupil_size = 4
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
            
            # Draw cosmic eye highlights (Mars symbol)
            self.canvas.create_text(
                left_eye_x, eye_y - 2,
                text=self.mars_symbol, fill='#FFFFFF', font=("Arial", 6)
            )
            self.canvas.create_text(
                right_eye_x, eye_y - 2,
                text=self.mars_symbol, fill='#FFFFFF', font=("Arial", 6)
            )
        else:
            # Draw closed eyes
            self.canvas.create_arc(
                left_eye_x - self.eye_size, eye_y - 2,
                left_eye_x + self.eye_size, eye_y + 2,
                start=0, extent=-180, style=tk.ARC, 
                outline='#2F2F2F', width=3
            )
            self.canvas.create_arc(
                right_eye_x - self.eye_size, eye_y - 2,
                right_eye_x + self.eye_size, eye_y + 2,
                start=0, extent=-180, style=tk.ARC, 
                outline='#2F2F2F', width=3
            )
        
        # Draw cosmic mouth (slight smile)
        mouth_y = draw_y + 20
        self.canvas.create_arc(
            draw_x - self.mouth_width, 
            mouth_y - self.mouth_height//2,
            draw_x + self.mouth_width, 
            mouth_y + self.mouth_height//2,
            start=10, extent=-160, style=tk.ARC, 
            fill='', outline=self.mouth_color, width=2
        )
        
        # Draw elaborate cosmic wings
        wing_offset = math.sin(self.wing_phase) * 6
        
        # Left cosmic wing with Mars details
        left_wing_points = [
            draw_x - 55, draw_y - 18 + wing_offset,
            draw_x - 65, draw_y - 30,
            draw_x - 58, draw_y + 5,
            draw_x - 48, draw_y - 10
        ]
        self.canvas.create_polygon(
            left_wing_points, fill=self.wing_color, outline=self.wing_edge, width=2
        )
        
        # Right cosmic wing with Mars details
        right_wing_points = [
            draw_x + 55, draw_y - 18 - wing_offset,
            draw_x + 65, draw_y - 30,
            draw_x + 58, draw_y + 5,
            draw_x + 48, draw_y - 10
        ]
        self.canvas.create_polygon(
            right_wing_points, fill=self.wing_color, outline=self.wing_edge, width=2
        )
        
        # Add cosmic details to wings
        self.canvas.create_text(
            draw_x - 55, draw_y - 10 + wing_offset,
            text=self.mars_symbol, fill=self.wing_edge, font=("Arial", 10)
        )
        self.canvas.create_text(
            draw_x + 55, draw_y - 10 - wing_offset,
            text=self.mars_symbol, fill=self.wing_edge, font=("Arial", 10)
        )
        
        # Draw decorative cosmic elements around the fairy
        for i in range(8):
            angle = (i * 45) * math.pi / 180
            distance = self.body_radius + 15
            x = draw_x + distance * math.cos(angle)
            y = draw_y + distance * math.sin(angle)
            self.canvas.create_text(
                x, y, text="✦", fill='#A1C4FD', font=("Arial", 12)
            )
    
    def on_drag_start(self, event):
        """Begin dragging the fairy - but MIST can override"""
        self.drag_data = {"x": event.x, "y": event.y, "start_x": self.x, "start_y": self.y}
    
    def on_drag(self, event):
        """Handle dragging the fairy - but MIST can override"""
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        new_x = self.drag_data["start_x"] + dx
        new_y = self.drag_data["start_y"] + dy
        
        # Update current position to match drag
        self.current_x = new_x + 110
        self.current_y = new_y + 110
        
        # Update target position to match drag
        self.target_x = self.current_x
        self.target_y = self.current_y
        
        self.x = new_x
        self.y = new_y
        self.root.geometry(f"220x220+{self.x}+{self.y}")
    
    def on_drag_stop(self, event):
        """Stop dragging the fairy"""
        pass
    
    def animate(self):
        """Detailed cosmic animation with controlled movement"""
        # Process any pending commands
        self.process_commands()
        
        # Handle blinking
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            if random.randint(0, 120) == 0:  # Less frequent blinking
                self.blink_state = False
                self.blink_timer = 20
        
        # Wing animation
        self.wing_phase += 0.15  # Gentle wing movement
        
        # Float animation (cosmic drifting)
        self.float_offset = math.sin(time.time() * 1.5) * 3  # Gentle floating
        
        # Pulse animation
        self.pulse_phase += 0.1
        
        # Cosmic phase animation
        self.cosmic_phase += 0.05
        
        # State timer
        if self.state_timer > 0:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.visual_mode = "normal"
        
        # Smooth movement toward target position
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        
        # Move towards target with smooth interpolation
        self.current_x += dx * self.move_speed
        self.current_y += dy * self.move_speed
        
        # Update window position based on current position
        self.x = int(self.current_x - 110)
        self.y = int(self.current_y - 110)
        self.root.geometry(f"220x220+{self.x}+{self.y}")
        
        # Add cosmic elements
        # Add distant stars occasionally
        if len(self.stars) < 30 and random.randint(0, 8) == 0:
            x = random.randint(10, 210)
            y = random.randint(10, 210)
            brightness = random.randint(150, 255)
            size = random.randint(1, 2)
            self.stars.append((x, y, brightness, size))
        
        # Add Mars particles
        if len(self.mars_particles) < 20 and random.randint(0, 6) == 0:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(50, 100)
            px = 110 + distance * math.cos(angle)
            py = 110 + self.float_offset + distance * math.sin(angle)
            self.mars_particles.append((px, py, 0, random.randint(2, 4)))
        
        # Add cosmic trails
        if len(self.cosmic_trails) < 25 and random.randint(0, 5) == 0:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(30, 70)
            cx = 110 + distance * math.cos(angle)
            cy = 110 + self.float_offset + distance * math.sin(angle)
            self.cosmic_trails.append((cx, cy, 0, random.randint(1, 3)))
        
        # Remove excess cosmic elements to maintain performance
        if len(self.stars) > 30:
            self.stars.pop(0)
        if len(self.mars_particles) > 20:
            self.mars_particles.pop(0)
        if len(self.cosmic_trails) > 25:
            self.cosmic_trails.pop(0)
        
        # Redraw fairy
        self.draw_fairy()
        
        # Schedule next animation frame
        self.root.after(30, self.animate)
    
    def run(self):
        """Start the fairy system"""
        self.root.mainloop()


# Global instance for external control
mist_controlled_fairy = None


def move_fairy_to(x, y):
    """Move the fairy to a specific position"""
    global mist_controlled_fairy
    if mist_controlled_fairy:
        mist_controlled_fairy.set_position(x, y)


def set_fairy_mode(mode):
    """Set the visual mode of the fairy"""
    global mist_controlled_fairy
    if mist_controlled_fairy:
        mist_controlled_fairy.set_visual_mode(mode)


def main():
    global mist_controlled_fairy
    print("Starting MIST-Controlled Fairy...")
    print("Features:")
    print("- Detailed ethereal goddess design with Mars/cosmic elements")
    print("- Full MIST automation with position and mode control")
    print("- Click and drag capability (MIST can override)")
    print("- Multiple visual modes: normal, observing, searching, focused")
    print("- Smooth, controlled movement")
    print("- Cosmic particles and effects")
    
    mist_controlled_fairy = MISTControlledFairy()
    mist_controlled_fairy.run()


if __name__ == "__main__":
    main()