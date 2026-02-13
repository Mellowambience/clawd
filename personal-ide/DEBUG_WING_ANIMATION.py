"""
Debug Version to Test Wing Animation
"""

import tkinter as tk
import math
import time
import random


class DebugWingAnimation:
    def __init__(self):
        # Create a transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("Debug Wing Animation Test")
        
        # Set transparency and attributes
        self.root.configure(bg='white')
        self.root.attributes('-transparentcolor', 'white')  # Make white transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations
        
        # Size the window appropriately for the fairy
        self.root.geometry("180x180")
        
        # Position fairy initially in upper right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - 200
        self.y = 50
        self.root.geometry(f"180x180+{self.x}+{self.y}")
        
        # Create canvas for drawing the fairy
        self.canvas = tk.Canvas(
            self.root,
            width=180,
            height=180,
            bg='white',  # This will be transparent
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Properties
        self.orb_radius = 35
        self.eye_size = 7
        self.mouth_width = 8
        self.mouth_height = 4
        
        # Color palette
        self.orb_color = '#F0E6FF'
        self.eye_color = '#6B8E23'
        self.mouth_color = '#FADADD'
        self.wing_color = '#E6E6FA'
        self.cheek_color = '#FFD1DC'
        self.party_hat_color = '#FFD700'
        
        # Animation and behavior properties
        self.blink_state = True
        self.blink_timer = 0
        self.head_tilt = 0
        self.wing_flap_counter = 0  # Counter to track wing animation
        self.visible = True
        
        # Draw initial fairy
        self.draw_fairy()
        
        # Start animation
        self.animate()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
    
    def draw_fairy(self):
        """Draw the fairy with debug wing animation"""
        self.canvas.delete("all")
        
        if not self.visible:
            return
        
        # Calculate position for drawing
        draw_x, draw_y = 90, 90  # Center in canvas
        
        # Print debug information
        print(f"Wing flap counter: {self.wing_flap_counter}, Time: {time.time()}")
        
        # Draw the orb body (round, softly imperfect)
        self.canvas.create_oval(
            draw_x - self.orb_radius, 
            draw_y - self.orb_radius, 
            draw_x + self.orb_radius, 
            draw_y + self.orb_radius,
            fill=self.orb_color, outline='#E0D0F0', width=1
        )
        
        # Draw subtle texture on orb (hand-crafted feel)
        for i in range(6):
            angle = (i * 60) * math.pi / 180
            x = draw_x + (self.orb_radius - 8) * math.cos(angle)
            y = draw_y + (self.orb_radius - 8) * math.sin(angle)
            self.canvas.create_oval(x-1, y-1, x+1, y+1, fill='#E6E6FA', outline='')
        
        # Draw rosy cheeks (adjusted for smaller size)
        self.canvas.create_oval(
            draw_x - 20, draw_y + 2,
            draw_x - 14, draw_y + 6,
            fill=self.cheek_color, outline='', stipple=''
        )
        self.canvas.create_oval(
            draw_x + 14, draw_y + 2,
            draw_x + 20, draw_y + 6,
            fill=self.cheek_color, outline='', stipple=''
        )
        
        # Draw large expressive green eyes (quiet awareness)
        left_eye_x = draw_x - 15
        right_eye_x = draw_x + 15
        eye_y = draw_y - 5
        
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
                left_eye_x - 2, eye_y - 1.5,
                left_eye_x + 1, eye_y + 0.5,
                fill='#2F2F2F', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 2, eye_y - 1.5,
                right_eye_x + 1, eye_y + 0.5,
                fill='#2F2F2F', outline='', width=1
            )
            
            # Subtle eye highlights (not flashy)
            self.canvas.create_oval(
                left_eye_x - 0.8, eye_y - 0.8,
                left_eye_x, eye_y,
                fill='#F0F0F0', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 0.8, eye_y - 0.8,
                right_eye_x, eye_y,
                fill='#F0F0F0', outline='', width=1
            )
        else:
            # Draw closed eyes (sleepy, gentle)
            self.canvas.create_arc(
                left_eye_x - self.eye_size, eye_y - 1.5,
                left_eye_x + self.eye_size, eye_y + 1.5,
                start=0, extent=-180, style=tk.ARC, 
                outline='#2F2F2F', width=2
            )
            self.canvas.create_arc(
                right_eye_x - self.eye_size, eye_y - 1.5,
                right_eye_x + self.eye_size, eye_y + 1.5,
                start=0, extent=-180, style=tk.ARC, 
                outline='#2F2F2F', width=2
            )
        
        # Draw minimal mouth (restrained expression)
        mouth_y = draw_y + 15
        self.canvas.create_arc(
            draw_x - self.mouth_width//2, 
            mouth_y - self.mouth_height//4,
            draw_x + self.mouth_width//2, 
            mouth_y + self.mouth_height//4,
            start=10, extent=-160, style=tk.ARC, 
            fill='', outline=self.mouth_color, width=1
        )
        
        # Draw organic wings (light lavender, semi-translucent) - BIGGER WINGS WITH ANIMATION
        # Use the wing_flap_counter to create animation
        wing_offset = math.sin(self.wing_flap_counter * 0.2) * 3  # More pronounced wing movement
        
        # Left wing - bigger for more dramatic effect
        left_wing_points = [
            draw_x - 55, draw_y - 20 + wing_offset,  # Bigger
            draw_x - 70, draw_y - 35,
            draw_x - 58, draw_y + 5,
            draw_x - 45, draw_y - 8
        ]
        self.canvas.create_polygon(
            left_wing_points, fill=self.wing_color, outline='', stipple=''
        )
        
        # Right wing - bigger for more dramatic effect
        right_wing_points = [
            draw_x + 55, draw_y - 20 - wing_offset,  # Bigger
            draw_x + 70, draw_y - 35,
            draw_x + 58, draw_y + 5,
            draw_x + 45, draw_y - 8
        ]
        self.canvas.create_polygon(
            right_wing_points, fill=self.wing_color, outline='', stipple=''
        )
        
        # Draw tiny whimsical party hat (slightly worn, tilted) - even smaller for smaller body
        hat_x = draw_x + 3
        hat_y = draw_y - 15 + self.head_tilt * 1.5
        hat_points = [
            hat_x, hat_y - 8,
            hat_x - 5, hat_y - 2,
            hat_x + 5, hat_y - 2,
        ]
        self.canvas.create_polygon(
            hat_points, fill=self.party_hat_color, outline='#D4AF37', width=1
        )
        
        # Draw hat decoration - smaller
        self.canvas.create_oval(
            hat_x - 1, hat_y - 6, hat_x + 1, hat_y - 4,
            fill='#FF69B4', outline=''
        )
    
    def animate(self):
        """Animate with debug output"""
        # Handle blinking
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            if random.randint(0, 60) == 0:  # Blink approximately every 1-2 seconds
                self.blink_state = False
                self.blink_timer = 15
        
        # Increment wing flap counter for animation
        self.wing_flap_counter += 1
        
        # Very occasional head tilt
        if random.randint(0, 300) == 0:
            self.head_tilt = random.choice([-1, 1])
            # Reset after a while
            self.root.after(600, self.reset_head_tilt)
        
        # Redraw fairy
        self.draw_fairy()
        
        # Schedule next animation frame
        self.root.after(30, self.animate)  # ~33 FPS
    
    def reset_head_tilt(self):
        """Reset the head tilt"""
        self.head_tilt = 0
    
    def on_drag_start(self, event):
        """Begin dragging the fairy"""
        self.drag_data = {"x": event.x, "y": event.y, "start_x": self.x, "start_y": self.y}
    
    def on_drag(self, event):
        """Handle dragging the fairy"""
        # Calculate new position
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        new_x = self.drag_data["start_x"] + dx
        new_y = self.drag_data["start_y"] + dy
        
        # Update position
        self.x = new_x
        self.y = new_y
        self.root.geometry(f"180x180+{self.x}+{self.y}")
    
    def on_drag_stop(self, event):
        """Stop dragging the fairy"""
        pass
    
    def run(self):
        """Start the fairy system"""
        self.root.mainloop()


def main():
    print("Starting Debug Wing Animation Test...")
    print("This version prints debug info to console.")
    print("Look for 'Wing flap counter' messages to verify animation is running.")
    
    companion = DebugWingAnimation()
    companion.run()


if __name__ == "__main__":
    main()