"""
Orbital Fairy MIST - Refined Appearance with Orbiting Movement
"""

import tkinter as tk
import math
import time
import random


class OrbitalFairyMist:
    def __init__(self):
        # Create a transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("Orbital Fairy MIST")
        
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
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        self.orbit_radius = min(screen_width, screen_height) // 3  # Orbit radius
        self.orbit_angle = 0  # Starting angle
        self.x = self.center_x + self.orbit_radius - 90  # Start at right side of orbit
        self.y = self.center_y - 90
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
        
        # Properties - Refined appearance
        self.orb_radius = 30  # Smaller, more delicate
        self.eye_size = 6     # Smaller eyes for refined look
        self.mouth_width = 6  # Smaller mouth
        self.mouth_height = 3
        
        # Refined color palette (softer, more harmonious)
        self.orb_color = '#F8F4FF'  # Very soft lavender-white
        self.eye_color = '#7DAF46'  # Softer green (less harsh)
        self.mouth_color = '#FFEAEA'  # Very light pink
        self.wing_color = '#F0F0FF'  # Softer lavender-blue
        self.cheek_color = '#FFE6F0'  # Softer pink
        self.party_hat_color = '#FFFACD'  # Softer gold
        self.outline_color = '#E6E6FA'  # Subtle outline
        
        # Animation and behavior properties
        self.blink_state = True
        self.blink_timer = 0
        self.head_tilt = 0
        self.wing_phase = 0  # Phase for wing animation
        self.visible = True
        
        # Orbital movement properties
        self.orbit_speed = 0.005  # Slow, gentle orbit
        
        # Draw initial fairy
        self.draw_fairy()
        
        # Start animation
        self.animate()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
    
    def draw_fairy(self):
        """Draw the fairy with refined appearance"""
        self.canvas.delete("all")
        
        if not self.visible:
            return
        
        # Calculate position for drawing
        draw_x, draw_y = 90, 90  # Center in canvas
        
        # Draw the orb body (round, softly imperfect with refined colors)
        self.canvas.create_oval(
            draw_x - self.orb_radius, 
            draw_y - self.orb_radius, 
            draw_x + self.orb_radius, 
            draw_y + self.orb_radius,
            fill=self.orb_color, outline=self.outline_color, width=1
        )
        
        # Draw subtle texture on orb (hand-crafted feel)
        for i in range(5):
            angle = (i * 72) * math.pi / 180
            x = draw_x + (self.orb_radius - 6) * math.cos(angle)
            y = draw_y + (self.orb_radius - 6) * math.sin(angle)
            self.canvas.create_oval(x-0.8, y-0.8, x+0.8, y+0.8, fill='#F0F0FF', outline='')
        
        # Draw refined rosy cheeks (more subtle)
        self.canvas.create_oval(
            draw_x - 16, draw_y + 1,
            draw_x - 11, draw_y + 5,
            fill=self.cheek_color, outline='', stipple=''
        )
        self.canvas.create_oval(
            draw_x + 11, draw_y + 1,
            draw_x + 16, draw_y + 5,
            fill=self.cheek_color, outline='', stipple=''
        )
        
        # Draw refined green eyes (gentle awareness)
        left_eye_x = draw_x - 12
        right_eye_x = draw_x + 12
        eye_y = draw_y - 4
        
        if self.blink_state:
            # Draw open eyes with refined expression
            self.canvas.create_oval(
                left_eye_x - self.eye_size, eye_y - self.eye_size,
                left_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#D9D9D9', width=1
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size, eye_y - self.eye_size,
                right_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#D9D9D9', width=1
            )
            
            # Draw refined green irises
            self.canvas.create_oval(
                left_eye_x - self.eye_size * 0.5, eye_y - self.eye_size * 0.5,
                left_eye_x + self.eye_size * 0.5, eye_y + self.eye_size * 0.5,
                fill=self.eye_color, outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size * 0.5, eye_y - self.eye_size * 0.5,
                right_eye_x + self.eye_size * 0.5, eye_y + self.eye_size * 0.5,
                fill=self.eye_color, outline='', width=1
            )
            
            # Draw pupils
            self.canvas.create_oval(
                left_eye_x - 1.5, eye_y - 1,
                left_eye_x + 0.5, eye_y + 1,
                fill='#333333', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 1.5, eye_y - 1,
                right_eye_x + 0.5, eye_y + 1,
                fill='#333333', outline='', width=1
            )
            
            # Subtle eye highlights (very subtle)
            self.canvas.create_oval(
                left_eye_x - 0.5, eye_y - 0.5,
                left_eye_x, eye_y,
                fill='#F8F8F8', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 0.5, eye_y - 0.5,
                right_eye_x, eye_y,
                fill='#F8F8F8', outline='', width=1
            )
        else:
            # Draw closed eyes (sleepy, gentle)
            self.canvas.create_arc(
                left_eye_x - self.eye_size, eye_y - 1,
                left_eye_x + self.eye_size, eye_y + 1,
                start=0, extent=-180, style=tk.ARC, 
                outline='#333333', width=1.5
            )
            self.canvas.create_arc(
                right_eye_x - self.eye_size, eye_y - 1,
                right_eye_x + self.eye_size, eye_y + 1,
                start=0, extent=-180, style=tk.ARC, 
                outline='#333333', width=1.5
            )
        
        # Draw refined minimal mouth (very subtle)
        mouth_y = draw_y + 12
        self.canvas.create_arc(
            draw_x - self.mouth_width//2, 
            mouth_y - self.mouth_height//4,
            draw_x + self.mouth_width//2, 
            mouth_y + self.mouth_height//4,
            start=15, extent=-150, style=tk.ARC, 
            fill='', outline=self.mouth_color, width=0.8
        )
        
        # Draw refined organic wings (gentle movement)
        wing_offset = math.sin(self.wing_phase) * 6  # Refined wing movement
        
        # Left wing - refined shape
        left_wing_points = [
            draw_x - 45, draw_y - 15 + wing_offset,
            draw_x - 60, draw_y - 30,
            draw_x - 50, draw_y + 3,
            draw_x - 38, draw_y - 5
        ]
        self.canvas.create_polygon(
            left_wing_points, fill=self.wing_color, outline='#E6E6F5', width=0.5
        )
        
        # Right wing - refined shape
        right_wing_points = [
            draw_x + 45, draw_y - 15 - wing_offset,
            draw_x + 60, draw_y - 30,
            draw_x + 50, draw_y + 3,
            draw_x + 38, draw_y - 5
        ]
        self.canvas.create_polygon(
            right_wing_points, fill=self.wing_color, outline='#E6E6F5', width=0.5
        )
        
        # Draw refined tiny whimsical party hat (subtle)
        hat_x = draw_x + 2
        hat_y = draw_y - 12 + self.head_tilt * 1
        hat_points = [
            hat_x, hat_y - 6,
            hat_x - 4, hat_y - 1,
            hat_x + 4, hat_y - 1,
        ]
        self.canvas.create_polygon(
            hat_points, fill=self.party_hat_color, outline='#EEE8AA', width=0.8
        )
        
        # Draw refined hat decoration
        self.canvas.create_oval(
            hat_x - 0.8, hat_y - 4.5, hat_x + 0.8, hat_y - 3,
            fill='#FFB6C1', outline=''
        )
    
    def animate(self):
        """Animate with orbital movement and refined behavior"""
        # Handle blinking
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            # Random blinking, more refined timing
            if random.randint(0, 90) == 0:  # Less frequent blinking
                self.blink_state = False
                self.blink_timer = 12  # Shorter blink duration
        
        # Increment wing phase for animation
        self.wing_phase += 0.12  # Refined wing speed
        
        # Very rare head tilt (more refined)
        if random.randint(0, 600) == 0:  # Much rarer head tilt
            self.head_tilt = random.choice([-0.8, 0.8])  # Subtle tilt
            # Reset after a while
            self.root.after(400, self.reset_head_tilt)
        
        # Update orbital position
        self.orbit_angle += self.orbit_speed
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate new position based on orbit
        new_x = self.center_x + self.orbit_radius * math.cos(self.orbit_angle) - 90
        new_y = self.center_y + self.orbit_radius * 0.6 * math.sin(self.orbit_angle) - 90  # Elliptical orbit
        
        # Keep within screen bounds
        new_x = max(0, min(screen_width - 180, new_x))
        new_y = max(0, min(screen_height - 180, new_y))
        
        # Update position
        self.x = new_x
        self.y = new_y
        self.root.geometry(f"180x180+{int(self.x)}+{int(self.y)}")
        
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
        
        # Update orbit center when dragged significantly
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.center_x = self.x + 90
        self.center_y = self.y + 90
        
    def on_drag_stop(self, event):
        """Stop dragging the fairy"""
        pass
    
    def run(self):
        """Start the fairy system"""
        self.root.mainloop()


def main():
    print("Starting Orbital Fairy MIST...")
    print("Features:")
    print("- Orbital movement around screen center")
    print("- Refined, softer appearance")
    print("- Gentle, elliptical orbit path")
    print("- Subtle wing animation")
    
    fairy_mist = OrbitalFairyMist()
    fairy_mist.run()


if __name__ == "__main__":
    main()