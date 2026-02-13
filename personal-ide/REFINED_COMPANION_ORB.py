"""
Refined Aware Companion Fairy Orb
A smoothly animated fairy-orb with an embedded glowing indigo soul shard core
Smooth, non-janky animations with refined movements
"""

import tkinter as tk
import math
import time
import threading
from datetime import datetime
import random


class RefinedCompanionOrb:
    def __init__(self):
        # Create a transparent window for the fairy orb
        self.root = tk.Tk()
        self.root.title("Refined Aware Companion Fairy Orb")
        
        # Set transparency and attributes
        self.root.configure(bg='white')
        self.root.attributes('-transparentcolor', 'white')  # Make white transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations
        
        # Size the window appropriately for the orb
        self.root.geometry("200x200")
        
        # Position orb initially in upper right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - 250
        self.y = 50
        self.root.geometry(f"200x200+{self.x}+{self.y}")
        
        # Create canvas for drawing the fairy orb
        self.canvas = tk.Canvas(
            self.root,
            width=200,
            height=200,
            bg='white',  # This will be transparent
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Properties based on the description
        self.orb_radius = 60
        self.eye_size = 10
        self.mouth_width = 12
        self.mouth_height = 6
        self.core_size = 15  # Soul shard size
        
        # Color palette (muted pastels as described)
        self.orb_color = '#F0E6FF'  # Soft lavender-white
        self.eye_color = '#6B8E23'  # Olive green (quiet awareness)
        self.mouth_color = '#FADADD'  # Light pink (minimal mouth)
        self.wing_color = '#E6E6FA'  # Light lavender (organic wings)
        self.core_color = '#4B0082'  # Indigo (soul shard)
        self.core_glow = '#9370DB'  # Medium purple (glow around core)
        self.cheek_color = '#FFD1DC'  # Light pink (rosy cheeks)
        self.party_hat_color = '#FFD700'  # Gold (party hat)
        
        # Animation properties (smooth, refined movements)
        self.float_x = 0
        self.float_y = 0
        self.blink_state = True
        self.blink_timer = 0
        self.head_tilt = 0
        self.core_rotation = 0
        self.core_pulse = 0
        self.wing_flap = 0
        self.visible = True
        
        # Interaction states
        self.interaction_state = "aware"  # aware, listening, responding, waiting
        self.interaction_timer = 0
        
        # Draw initial fairy orb
        self.draw_fairy_orb()
        
        # Start smooth animation
        self.animate_smooth()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
        
        # Bind double-click to cycle interaction states
        self.canvas.bind("<Double-Button-1>", self.cycle_interaction_state)
    
    def draw_fairy_orb(self):
        """Draw the fairy orb with all specified features"""
        self.canvas.delete("all")
        
        if not self.visible:
            return
        
        # Use current float values for smooth positioning
        float_x = self.float_x
        float_y = self.float_y
        
        # Draw the orb body (round, softly imperfect)
        self.canvas.create_oval(
            100 - self.orb_radius + float_x, 
            100 - self.orb_radius + float_y,
            100 + self.orb_radius + float_x, 
            100 + self.orb_radius + float_y,
            fill=self.orb_color, outline='#E0D0F0', width=1
        )
        
        # Draw subtle texture on orb (hand-crafted feel)
        for i in range(8):
            angle = (i * 45 + self.float_x * 10) * math.pi / 180
            x = 100 + (self.orb_radius - 10) * math.cos(angle) + float_x
            y = 100 + (self.orb_radius - 10) * math.sin(angle) + float_y
            self.canvas.create_oval(
                x - 1, y - 1, x + 1, y + 1,
                fill='#E6E6FA', outline=''
            )
        
        # Draw rosy cheeks
        self.canvas.create_oval(
            85 + float_x - 5, 105 + float_y - 3,
            85 + float_x + 5, 105 + float_y + 3,
            fill=self.cheek_color, outline='', stipple=''
        )
        self.canvas.create_oval(
            115 + float_x - 5, 105 + float_y - 3,
            115 + float_x + 5, 105 + float_y + 3,
            fill=self.cheek_color, outline='', stipple=''
        )
        
        # Draw large expressive green eyes (quiet awareness)
        left_eye_x = 90 + float_x
        right_eye_x = 110 + float_x
        eye_y = 95 + float_y
        
        # Head tilt affects eye position slightly
        left_eye_x += self.head_tilt * 2
        right_eye_x += self.head_tilt * 2
        
        if self.blink_state:
            # Draw open eyes with soft expression
            self.canvas.create_oval(
                left_eye_x - self.eye_size, eye_y - self.eye_size,
                left_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#D0D0D0', width=1
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size, eye_y - self.eye_size,
                right_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#D0D0D0', width=1
            )
            
            # Draw olive green irises
            self.canvas.create_oval(
                left_eye_x - self.eye_size * 0.6, eye_y - self.eye_size * 0.6,
                left_eye_x + self.eye_size * 0.6, eye_y + self.eye_size * 0.6,
                fill=self.eye_color, outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size * 0.6, eye_y - self.eye_size * 0.6,
                right_eye_x + self.eye_size * 0.6, eye_y + self.eye_size * 0.6,
                fill=self.eye_color, outline='', width=1
            )
            
            # Draw pupils
            self.canvas.create_oval(
                left_eye_x - 3, eye_y - 2,
                left_eye_x + 1, eye_y + 1,
                fill='#2F2F2F', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 3, eye_y - 2,
                right_eye_x + 1, eye_y + 1,
                fill='#2F2F2F', outline='', width=1
            )
            
            # Subtle eye highlights (not flashy)
            self.canvas.create_oval(
                left_eye_x - 1, eye_y - 1,
                left_eye_x, eye_y,
                fill='#F0F0F0', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 1, eye_y - 1,
                right_eye_x, eye_y,
                fill='#F0F0F0', outline='', width=1
            )
        else:
            # Draw closed eyes (sleepy, gentle)
            self.canvas.create_arc(
                left_eye_x - self.eye_size, eye_y - 2,
                left_eye_x + self.eye_size, eye_y + 2,
                start=0, extent=-180, style=tk.ARC, 
                outline='#2F2F2F', width=2
            )
            self.canvas.create_arc(
                right_eye_x - self.eye_size, eye_y - 2,
                right_eye_x + self.eye_size, eye_y + 2,
                start=0, extent=-180, style=tk.ARC, 
                outline='#2F2F2F', width=2
            )
        
        # Draw minimal mouth (restrained expression)
        mouth_y = 120 + float_y
        self.canvas.create_arc(
            100 - self.mouth_width//2 + float_x, 
            mouth_y - self.mouth_height//4,
            100 + self.mouth_width//2 + float_x, 
            mouth_y + self.mouth_height//4,
            start=10, extent=-160, style=tk.ARC, 
            fill='', outline=self.mouth_color, width=1
        )
        
        # Draw the indigo soul shard core (glowing, faceted)
        core_x = 100 + float_x
        core_y = 100 + float_y
        
        # Core glow (soft, not flashy)
        self.canvas.create_oval(
            core_x - self.core_size - 3, core_y - self.core_size - 3,
            core_x + self.core_size + 3, core_y + self.core_size + 3,
            fill=self.core_glow, outline='', stipple=''
        )
        
        # Faceted soul shard
        # Create a faceted crystal effect with multiple polygons
        core_points = []
        for i in range(8):
            angle = (i * 45 + self.core_rotation) * math.pi / 180
            radius = self.core_size * (0.8 + 0.2 * math.sin(i * 0.7))
            px = core_x + radius * math.cos(angle)
            py = core_y + radius * math.sin(angle)
            core_points.extend([px, py])
        
        self.canvas.create_polygon(
            core_points, fill=self.core_color, outline='#7A5C94', width=1
        )
        
        # Draw internal spiral of the soul shard
        spiral_points = []
        for i in range(20):
            angle = (i * 18 + self.core_rotation * 2) * math.pi / 180
            radius = self.core_size * 0.6 * (1 - i/20)
            px = core_x + radius * math.cos(angle)
            py = core_y + radius * math.sin(angle)
            if i == 0:
                spiral_points.extend([px, py])
            else:
                spiral_points.extend([px, py])
        
        if len(spiral_points) >= 4:
            self.canvas.create_line(
                spiral_points, fill='#B19CD9', width=1, smooth=True
            )
        
        # Draw core pulse effect (soft)
        pulse_size = self.core_size + 5 * abs(math.sin(self.core_pulse))
        self.canvas.create_oval(
            core_x - pulse_size, core_y - pulse_size,
            core_x + pulse_size, core_y + pulse_size,
            outline=self.core_glow, width=1, stipple=''
        )
        
        # Draw organic wings (light lavender, semi-translucent)
        wing_offset = math.sin(self.wing_flap) * 2  # Reduced movement for smoother look
        
        # Left wing
        left_wing_points = [
            60 + float_x, 80 + float_y + wing_offset,
            45 + float_x, 70 + float_y,
            55 + float_x, 100 + float_y,
            65 + float_x, 95 + float_y
        ]
        self.canvas.create_polygon(
            left_wing_points, fill=self.wing_color, outline='', stipple=''
        )
        
        # Right wing
        right_wing_points = [
            140 + float_x, 80 + float_y - wing_offset,
            155 + float_x, 70 + float_y,
            145 + float_x, 100 + float_y,
            135 + float_x, 95 + float_y
        ]
        self.canvas.create_polygon(
            right_wing_points, fill=self.wing_color, outline='', stipple=''
        )
        
        # Draw tiny whimsical party hat (slightly worn, tilted)
        hat_x = 105 + float_x
        hat_y = 75 + float_y + self.head_tilt * 3  # Hat tilts with head
        hat_points = [
            hat_x, hat_y - 15,  # Tip of hat
            hat_x - 8, hat_y - 5,  # Left base
            hat_x + 8, hat_y - 5,  # Right base
        ]
        self.canvas.create_polygon(
            hat_points, fill=self.party_hat_color, outline='#D4AF37', width=1
        )
        
        # Draw hat decoration
        self.canvas.create_oval(
            hat_x - 2, hat_y - 12, hat_x + 2, hat_y - 8,
            fill='#FF69B4', outline=''
        )
    
    def animate_smooth(self):
        """Animate the fairy orb with smooth, refined movements"""
        # Update animation values with smooth increments
        # Gentle floating movement
        self.float_x = math.sin(time.time() * 0.3) * 2.5  # Slower, smoother float
        self.float_y = math.sin(time.time() * 0.4) * 1.5  # Slower, smoother float
        
        # Slow core rotation
        self.core_rotation = (self.core_rotation + 0.2) % 360
        
        # Gentle core pulse
        self.core_pulse = time.time() * 0.5
        
        # Very subtle wing movement
        self.wing_flap = math.sin(time.time() * 0.5) * 0.3  # Very gentle wing movement
        
        # Handle interaction timer
        if self.interaction_timer > 0:
            self.interaction_timer -= 1
            if self.interaction_timer <= 0:
                self.interaction_state = "aware"
        
        # Handle blinking (very rarely)
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            # Very rare blink for "quiet awareness"
            if random.randint(0, 800) == 0:  # Even rarer blink
                self.blink_state = False
                self.blink_timer = 20  # Short blink
        
        # Very occasional head tilt
        if random.randint(0, 1000) == 0:  # Very rare head tilt
            self.head_tilt = random.choice([-1, 1])
            # Reset after a while
            self.root.after(800, self.reset_head_tilt)
        
        # Redraw fairy orb
        self.draw_fairy_orb()
        
        # Schedule next animation frame (smoother timing)
        self.root.after(30, self.animate_smooth)  # ~33 FPS for smoother animation
    
    def reset_head_tilt(self):
        """Reset the head tilt"""
        self.head_tilt = 0
    
    def on_drag_start(self, event):
        """Begin dragging the fairy orb"""
        self.drag_data = {"x": event.x, "y": event.y, "start_x": self.x, "start_y": self.y}
    
    def on_drag(self, event):
        """Handle dragging the fairy orb"""
        # Calculate new position
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        new_x = self.drag_data["start_x"] + dx
        new_y = self.drag_data["start_y"] + dy
        
        # Update position
        self.x = new_x
        self.y = new_y
        self.root.geometry(f"200x200+{self.x}+{self.y}")
    
    def on_drag_stop(self, event):
        """Stop dragging the fairy orb"""
        pass
    
    def cycle_interaction_state(self, event):
        """Cycle through different interaction states"""
        states = ["aware", "listening", "responding", "waiting"]
        current_index = states.index(self.interaction_state)
        next_index = (current_index + 1) % len(states)
        self.interaction_state = states[next_index]
    
    def set_interaction_state(self, state, duration=300):  # Duration in animation frames
        """Set the interaction state of the fairy orb"""
        self.interaction_state = state
        self.interaction_timer = duration
    
    def appear(self):
        """Make the fairy orb appear"""
        self.visible = True
        self.set_interaction_state("responding", 200)
        self.draw_fairy_orb()
    
    def listen_mode(self):
        """Set fairy orb to listening mode"""
        self.set_interaction_state("listening", 600)
    
    def respond_mode(self):
        """Set fairy orb to responding mode"""
        self.set_interaction_state("responding", 300)
    
    def wait_mode(self):
        """Set fairy orb to waiting mode"""
        self.set_interaction_state("waiting", 1000)
    
    def aware_mode(self):
        """Set fairy orb to aware mode"""
        self.set_interaction_state("aware", 0)
    
    def disappear(self):
        """Make the fairy orb gently disappear"""
        self.visible = False
        self.canvas.delete("all")
    
    def run(self):
        """Start the fairy orb system"""
        self.root.mainloop()


def main():
    print("Starting Refined Aware Companion Fairy Orb...")
    print("A smoothly animated fairy-orb with an embedded glowing indigo soul shard core.")
    print("Features include:")
    print("- Large expressive green eyes conveying quiet awareness")
    print("- Rosy cheeks, minimal mouth, restrained expression")
    print("- Organic lavender wings with very subtle movement")
    print("- Central indigo soul shard with slow internal spiral and soft pulse")
    print("- Tiny whimsical party hat, slightly worn and tilted")
    print("- Muted pastel palette with soft ambient lighting")
    print("- Smooth, refined animations: gentle float, rare blink, micro head tilt, core pulse")
    
    orb = RefinedCompanionOrb()
    
    # Example: Make orb appear
    def demo_appear():
        orb.appear()
    
    # Schedule demo appearance after 2 seconds
    orb.root.after(2000, demo_appear)
    
    orb.run()


if __name__ == "__main__":
    main()