"""
Eyes of MIST - Fairy controlled by MIST with visual indicators
"""

import tkinter as tk
import math
import time
import random


class EyesOfMIST:
    def __init__(self):
        # Create a transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("Eyes of MIST")
        
        # Set transparency and attributes
        self.root.configure(bg='white')
        self.root.attributes('-transparentcolor', 'white')  # Make white transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations
        
        # Size the window appropriately for the fairy
        self.root.geometry("200x200")
        
        # Position fairy in center of screen initially
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
        
        # Movement properties - controlled by MIST
        self.target_x = self.x + 100  # Center of fairy in screen coords
        self.target_y = self.y + 100  # Center of fairy in screen coords
        self.move_speed = 0.05  # Slower, smoother movement
        self.current_x = self.target_x
        self.current_y = self.target_y
        
        # Visual state properties
        self.visual_mode = "normal"  # "normal", "observing", "searching", "focused"
        self.state_timer = 0
        
        # Stable sparkle properties
        self.sparkles = []
        self.max_sparkles = 50  # Limit to prevent memory issues
        
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
    
    def draw_fairy(self):
        """Draw the fairy with visual indicators based on state"""
        self.canvas.delete("all")
        
        # Calculate position for drawing (center of canvas)
        draw_x, draw_y = 100, 100 + self.bounce_offset
        
        # Draw sparkles first (behind fairy)
        self._draw_sparkles(draw_x, draw_y)
        
        # Draw visual mode indicators
        self._draw_visual_mode_indicators(draw_x, draw_y)
        
        # Draw pulsing aura around the fairy
        self._draw_pulsing_aura(draw_x, draw_y)
        
        # Draw the orb body with gradient effect
        self._draw_orb_body(draw_x, draw_y)
        
        # Draw facial features
        self._draw_face(draw_x, draw_y)
        
        # Draw wings with more detail
        self._draw_wings(draw_x, draw_y)

    def _draw_sparkles(self, draw_x, draw_y):
        """Draw sparkles around the fairy"""
        # Process sparkles safely
        for i in range(len(self.sparkles)-1, -1, -1):  # Go backwards to safely remove
            if i >= len(self.sparkles):
                continue
            x, y, age, s_type, color, size = self.sparkles[i]
            
            # Update age
            self.sparkles[i] = (x, y, age + 1, s_type, color, size)
            
            # Remove old sparkles
            if age > 50:  # Remove after ~1.7 seconds
                self.sparkles.pop(i)
                continue
            
            # Draw sparkle based on type
            if s_type == "star":
                self.canvas.create_text(
                    x, y, text="★", fill=color, font=("Arial", size, "bold")
                )
            elif s_type == "heart":
                self.canvas.create_text(
                    x, y, text="♥", fill=color, font=("Arial", size, "bold")
                )
            elif s_type == "circle":
                self.canvas.create_oval(
                    x - size//2, y - size//2, x + size//2, y + size//2,
                    fill=color, outline=""
                )
            elif s_type == "diamond":
                self.canvas.create_text(
                    x, y, text="◆", fill=color, font=("Arial", size, "bold")
                )
            elif s_type == "plus":
                self.canvas.create_text(
                    x, y, text="+", fill=color, font=("Arial", size, "bold")
                )

    def _draw_visual_mode_indicators(self, draw_x, draw_y):
        """Draw visual indicators based on current mode"""
        if self.visual_mode == "observing":
            # Draw observing rings around the fairy
            for i in range(3):
                ring_size = self.orb_radius + 15 + i * 8 + int(3 * math.sin(self.pulse_phase + i))
                self.canvas.create_oval(
                    draw_x - ring_size, 
                    draw_y - ring_size, 
                    draw_x + ring_size, 
                    draw_y + ring_size,
                    outline='#32CD32', width=2, stipple='gray25'
                )
        elif self.visual_mode == "searching":
            # Draw searching spiral pattern
            for i in range(8):
                angle = self.pulse_phase + i * math.pi / 4
                dist = 30 + i * 5
                x = draw_x + dist * math.cos(angle)
                y = draw_y + dist * math.sin(angle)
                self.canvas.create_oval(
                    x - 3, y - 3, x + 3, y + 3,
                    fill='#FFD700', outline=''
                )
        elif self.visual_mode == "focused":
            # Draw focused beam effect
            self.canvas.create_line(
                draw_x, draw_y + self.orb_radius,
                draw_x, 180,
                fill='#4169E1', width=3, stipple='gray50'
            )
            # Draw focused eyes (more intense)
            self.canvas.create_oval(
                draw_x - 14 - self.eye_size, draw_y - 6 - self.eye_size,
                draw_x - 14 + self.eye_size, draw_y - 6 + self.eye_size,
                fill='white', outline='#FFD700', width=2
            )
            self.canvas.create_oval(
                draw_x + 14 - self.eye_size, draw_y - 6 - self.eye_size,
                draw_x + 14 + self.eye_size, draw_y - 6 + self.eye_size,
                fill='white', outline='#FFD700', width=2
            )

    def _draw_pulsing_aura(self, draw_x, draw_y):
        """Draw pulsing aura around the fairy"""
        pulse_size = self.orb_radius + 8 + int(6 * math.sin(self.pulse_phase))
        aura_color = '#9370DB'
        if self.visual_mode == "observing":
            aura_color = '#32CD32'
        elif self.visual_mode == "searching":
            aura_color = '#FFD700'
        elif self.visual_mode == "focused":
            aura_color = '#4169E1'
        
        self.canvas.create_oval(
            draw_x - pulse_size, 
            draw_y - pulse_size, 
            draw_x + pulse_size, 
            draw_y + pulse_size,
            outline=aura_color, width=2, stipple='gray25'
        )

    def _draw_orb_body(self, draw_x, draw_y):
        """Draw the orb body with gradient effect"""
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

    def _draw_face(self, draw_x, draw_y):
        """Draw the face of the fairy"""
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
        
        # Draw eyes with enhanced visual indicators
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
                right_eye_x - iris_size, eye_y - self.eye_size,
                right_eye_x + iris_size, eye_y + self.eye_size,
                fill=self.eye_color, outline='', width=1
            )
            
            # Draw pupils with shine
            pupil_size = 3
            self.canvas.create_oval(
                left_eye_x - pupil_size, eye_y - pupil_size,
                left_eye_x + pupil_size, eye_y + self.pupil_size,
                fill='#2F2F2F', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - pupil_size, eye_y - pupil_size,
                right_eye_x + pupil_size, eye_y + self.eye_size,
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

    def _draw_wings(self, draw_x, draw_y):
        """Draw wings with more detail"""
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
        """Animation with controlled movement"""
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
        self.x = int(self.current_x - 100)
        self.y = int(self.current_y - 100)
        self.root.geometry(f"200x200+{self.x}+{self.y}")
        
        # Add controlled sparkles - safer approach
        if len(self.sparkles) < self.max_sparkles and random.randint(0, 4) == 0:  # Very frequent but controlled
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
        
        # Redraw fairy
        self.draw_fairy()
        
        # Schedule next animation frame
        self.root.after(30, self.animate)
    
    def run(self):
        """Start the fairy system"""
        self.root.mainloop()


# Global instance for external control
mist_eyes = None


def move_fairy_to(x, y):
    """Move the fairy to a specific position"""
    global mist_eyes
    if mist_eyes:
        mist_eyes.set_position(x, y)


def set_fairy_mode(mode):
    """Set the visual mode of the fairy"""
    global mist_eyes
    if mist_eyes:
        mist_eyes.set_visual_mode(mode)


def main():
    global mist_eyes
    print("Starting Eyes of MIST...")
    print("Features:")
    print("- Controlled by MIST (not draggable)")
    print("- Visual modes: normal, observing, searching, focused")
    print("- Smooth movement to target positions")
    print("- Visual indicators for each mode")
    print("- Maximum stability and visual effects")
    
    mist_eyes = EyesOfMIST()
    mist_eyes.run()


if __name__ == "__main__":
    main()