"""
Cuter Fairy MIST - Adorable Design with Extra Charm
"""

import tkinter as tk
import math
import time
import random


class CuterFairyMist:
    def __init__(self):
        # Create a transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("Cuter Fairy MIST")
        
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
        
        # Properties - Extra cute design
        self.orb_radius = 35  # Rounder, cuter face
        self.eye_size = 9     # Bigger, cuter eyes
        self.mouth_width = 8  # Cuter mouth
        self.mouth_height = 4
        
        # Extra cute color palette (pastel, adorable)
        self.orb_color = '#FFF8F0'  # Soft cream-white (cute)
        self.eye_color = '#8B73A6'  # Soft purple-violet eyes (cute)
        self.mouth_color = '#FFD1DC'  # Pink (cute)
        self.wing_color = '#E6F3FF'  # Light blue wings (cute)
        self.cheek_color = '#FFB6C1'  # Brighter pink cheeks (cute)
        self.party_hat_color = '#FFD700'  # Gold (cute)
        self.outline_color = '#F0E6FF'  # Soft outline (cute)
        
        # Animation and behavior properties
        self.blink_state = True
        self.blink_timer = 0
        self.head_tilt = 0
        self.wing_phase = 0  # Phase for wing animation
        self.bounce_offset = 0  # For cute bouncing effect
        self.visible = True
        
        # Orbital movement properties
        self.orbit_speed = 0.006  # Gentle orbit
        
        # Draw initial fairy
        self.draw_fairy()
        
        # Start animation
        self.animate()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
    
    def draw_fairy(self):
        """Draw the fairy with extra cute design"""
        self.canvas.delete("all")
        
        if not self.visible:
            return
        
        # Calculate position for drawing with cute bounce
        draw_x, draw_y = 90, 90 + self.bounce_offset  # Add cute bounce
        
        # Draw the orb body (rounder, cuter face)
        self.canvas.create_oval(
            draw_x - self.orb_radius, 
            draw_y - self.orb_radius, 
            draw_x + self.orb_radius, 
            draw_y + self.orb_radius,
            fill=self.orb_color, outline=self.outline_color, width=2
        )
        
        # Draw cute blush circles on cheeks
        self.canvas.create_oval(
            draw_x - 22, draw_y + 5,
            draw_x - 12, draw_y + 12,
            fill=self.cheek_color, outline='', stipple=''
        )
        self.canvas.create_oval(
            draw_x + 12, draw_y + 5,
            draw_x + 22, draw_y + 12,
            fill=self.cheek_color, outline='', stipple=''
        )
        
        # Draw extra cute big eyes (wide-eyed wonder)
        left_eye_x = draw_x - 15  # Wider apart for cuteness
        right_eye_x = draw_x + 15
        eye_y = draw_y - 8  # Higher placement for baby face proportions
        
        if self.blink_state:
            # Draw big, round open eyes (super cute)
            self.canvas.create_oval(
                left_eye_x - self.eye_size, eye_y - self.eye_size,
                left_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#D0D0D0', width=1.5
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size, eye_y - self.eye_size,
                right_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#D0D0D0', width=1.5
            )
            
            # Draw big, cute purple-violet irises
            iris_size = self.eye_size * 0.6
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
            
            # Draw big, dark pupils
            pupil_size = self.eye_size * 0.3
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
            
            # Draw big, shiny eye highlights (extra cute)
            highlight_size = self.eye_size * 0.2
            self.canvas.create_oval(
                left_eye_x - highlight_size, eye_y - highlight_size*1.5,
                left_eye_x, eye_y - highlight_size*0.5,
                fill='#FFFFFF', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - highlight_size, eye_y - highlight_size*1.5,
                right_eye_x, eye_y - highlight_size*0.5,
                fill='#FFFFFF', outline='', width=1
            )
        else:
            # Draw cute closed eyes (sleepy cute)
            self.canvas.create_arc(
                left_eye_x - self.eye_size, eye_y - 2,
                left_eye_x + self.eye_size, eye_y + 2,
                start=0, extent=-180, style=tk.ARC, 
                outline='#2F2F2F', width=3  # Thicker for cute effect
            )
            self.canvas.create_arc(
                right_eye_x - self.eye_size, eye_y - 2,
                right_eye_x + self.eye_size, eye_y + 2,
                start=0, extent=-180, style=tk.ARC, 
                outline='#2F2F2F', width=3  # Thicker for cute effect
            )
        
        # Draw cute little mouth (tiny smile)
        mouth_y = draw_y + 18  # Lower placement for baby face
        self.canvas.create_arc(
            draw_x - self.mouth_width//2, 
            mouth_y - self.mouth_height//2,
            draw_x + self.mouth_width//2, 
            mouth_y + self.mouth_height//2,
            start=200, extent=140, style=tk.ARC, 
            fill='', outline=self.mouth_color, width=2  # Cuteness++
        )
        
        # Draw cute organic wings (fluffy, adorable)
        wing_offset = math.sin(self.wing_phase) * 7  # Cutesy wing flutter
        
        # Left wing - cute shape
        left_wing_points = [
            draw_x - 50, draw_y - 18 + wing_offset,
            draw_x - 65, draw_y - 32,
            draw_x - 53, draw_y + 2,
            draw_x - 42, draw_y - 6
        ]
        self.canvas.create_polygon(
            left_wing_points, fill=self.wing_color, outline='#D0E8FF', width=1
        )
        
        # Right wing - cute shape
        right_wing_points = [
            draw_x + 50, draw_y - 18 - wing_offset,
            draw_x + 65, draw_y - 32,
            draw_x + 53, draw_y + 2,
            draw_x + 42, draw_y - 6
        ]
        self.canvas.create_polygon(
            right_wing_points, fill=self.wing_color, outline='#D0E8FF', width=1
        )
        
        # Draw extra cute tiny party hat (adorable)
        hat_x = draw_x + 1  # Centered
        hat_y = draw_y - 18 + self.head_tilt * 0.5
        hat_points = [
            hat_x, hat_y - 8,  # Tip of hat
            hat_x - 5, hat_y - 2,  # Left base
            hat_x + 5, hat_y - 2,  # Right base
        ]
        self.canvas.create_polygon(
            hat_points, fill=self.party_hat_color, outline='#D4AF37', width=1
        )
        
        # Draw cute hat decoration (sparkle)
        self.canvas.create_oval(
            hat_x - 1.2, hat_y - 5.5, hat_x + 1.2, hat_y - 3.5,
            fill='#FFB6C1', outline=''
        )
        
        # Draw cute little sparkles occasionally
        if int(time.time()) % 4 < 1:  # Every 4 seconds for a bit
            sparkle_x = draw_x + random.randint(-20, 20)
            sparkle_y = draw_y - 40 + random.randint(-10, 10)
            self.canvas.create_text(
                sparkle_x, sparkle_y,
                text="★", fill='#FFD700', font=('Arial', 12, 'bold')
            )
    
    def animate(self):
        """Animate with cute behaviors"""
        # Handle blinking (more frequent for cute effect)
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            # Cute, frequent blinking
            if random.randint(0, 45) == 0:  # Blink more often (cute!)
                self.blink_state = False
                self.blink_timer = 8  # Quick blink (cute!)
        
        # Cute wing flutter
        self.wing_phase += 0.15  # Cute wing speed
        
        # Cute gentle bounce
        self.bounce_offset = math.sin(time.time() * 3) * 2  # Gentle bounce
        
        # Cute occasional head tilt (more frequent for cuteness)
        if random.randint(0, 200) == 0:  # More frequent head tilts (cute!)
            self.head_tilt = random.choice([-1.2, 1.2])
            # Reset after a while
            self.root.after(300, self.reset_head_tilt)
        
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
    print("Starting Cuter Fairy MIST...")
    print("Features:")
    print("- Bigger, rounder eyes for adorable look")
    print("- Rosier cheeks for extra cuteness")
    print("- Softer pastel colors")
    print("- Gentle bouncing animation")
    print("- More frequent cute blinks")
    print("- Sparkles and special effects")
    print("- All the orbital movement you love")
    
    fairy_mist = CuterFairyMist()
    fairy_mist.run()


if __name__ == "__main__":
    main()