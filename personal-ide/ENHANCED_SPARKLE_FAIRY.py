"""
Enhanced Sparkle Version of MIST Fairy - More Visual Elements
"""

import tkinter as tk
import math
import time
import random


class EnhancedSparkleFairy:
    def __init__(self):
        # Create a transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("Enhanced Sparkle MIST Fairy")
        
        # Set transparency and attributes
        self.root.configure(bg='white')
        self.root.attributes('-transparentcolor', 'white')  # Make white transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations
        
        # Size the window appropriately for the fairy
        self.root.geometry("180x180")
        
        # Position fairy in center of screen for visibility
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width // 2 - 90
        self.y = screen_height // 2 - 90
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
        
        # Simple fairy properties
        self.orb_radius = 30
        self.eye_size = 7
        self.mouth_width = 6
        self.mouth_height = 3
        
        # Simple color palette
        self.orb_color = '#F0F0FF'
        self.eye_color = '#5D3FD3'
        self.mouth_color = '#9370DB'
        
        # Animation properties
        self.blink_state = True
        self.blink_timer = 0
        self.wing_phase = 0
        self.bounce_offset = 0
        
        # Sparkle properties
        self.sparkles = []  # [(x, y, age, type), ...]
        
        # Simple orbital movement (for testing)
        self.orbit_angle = 0
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        self.orbit_radius = min(screen_width, screen_height) // 6  # Smaller orbit for testing
        
        # Draw initial fairy
        self.draw_fairy()
        
        # Start animation
        self.animate()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
    
    def draw_fairy(self):
        """Draw the fairy with enhanced elements"""
        self.canvas.delete("all")
        
        # Calculate position for drawing
        draw_x, draw_y = 90, 90 + self.bounce_offset
        
        # Draw background sparkles first (behind fairy)
        i = 0
        while i < len(self.sparkles):
            sx, sy, age, s_type = self.sparkles[i]
            # Update age
            self.sparkles[i] = (sx, sy, age + 1, s_type)
            
            # Remove old sparkles
            if age > 60:  # Remove after 2 seconds (30fps * 2)
                self.sparkles.pop(i)
                # Don't increment i since we removed an item
            else:
                i += 1
            
            # Draw sparkle based on type
            if s_type == "star":
                self.canvas.create_text(
                    sx, sy, text="★", fill="#FFD700", font=("Arial", 10, "bold")
                )
            elif s_type == "heart":
                self.canvas.create_text(
                    sx, sy, text="♥", fill="#FF69B4", font=("Arial", 10, "bold")
                )
            elif s_type == "circle":
                self.canvas.create_oval(
                    sx - 3, sy - 3, sx + 3, sy + 3,
                    fill="#9370DB", outline=""
                )
        
        # Draw the orb body
        self.canvas.create_oval(
            draw_x - self.orb_radius, 
            draw_y - self.orb_radius, 
            draw_x + self.orb_radius, 
            draw_y + self.orb_radius,
            fill=self.orb_color, outline='#D8BFD8', width=2
        )
        
        # Draw subtle texture on orb
        for i in range(6):
            angle = (i * 60) * math.pi / 180
            x = draw_x + (self.orb_radius - 6) * math.cos(angle)
            y = draw_y + (self.orb_radius - 6) * math.sin(angle)
            self.canvas.create_oval(x-1, y-1, x+1, y+1, fill='#E6E6FA', outline='')
        
        # Draw simple cheeks
        self.canvas.create_oval(
            draw_x - 16, draw_y + 3,
            draw_x - 10, draw_y + 8,
            fill='#DDA0DD', outline='', stipple=''
        )
        self.canvas.create_oval(
            draw_x + 10, draw_y + 3,
            draw_x + 16, draw_y + 8,
            fill='#DDA0DD', outline='', stipple=''
        )
        
        # Draw simple eyes
        left_eye_x = draw_x - 12
        right_eye_x = draw_x + 12
        eye_y = draw_y - 5
        
        if self.blink_state:
            # Draw open eyes
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
            
            # Draw irises
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
                left_eye_x - 2, eye_y - 2,
                left_eye_x + 1, eye_y + 1,
                fill='#2F2F2F', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 2, eye_y - 2,
                right_eye_x + 1, eye_y + 1,
                fill='#2F2F2F', outline='', width=1
            )
            
            # Draw eye highlights
            self.canvas.create_oval(
                left_eye_x - 0.8, eye_y - 1.5,
                left_eye_x, eye_y - 0.5,
                fill='#FFFFFF', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 0.8, eye_y - 1.5,
                right_eye_x, eye_y - 0.5,
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
        
        # Draw simple mouth
        mouth_y = draw_y + 14
        self.canvas.create_arc(
            draw_x - self.mouth_width//2, 
            mouth_y - self.mouth_height//4,
            draw_x + self.mouth_width//2, 
            mouth_y + self.mouth_height//4,
            start=15, extent=-150, style=tk.ARC, 
            fill='', outline=self.mouth_color, width=1.5
        )
        
        # Draw simple wings
        wing_offset = math.sin(self.wing_phase) * 4
        
        # Left wing
        left_wing_points = [
            draw_x - 40, draw_y - 12 + wing_offset,
            draw_x - 50, draw_y - 22,
            draw_x - 42, draw_y + 2,
            draw_x - 32, draw_y - 4
        ]
        self.canvas.create_polygon(
            left_wing_points, fill='#E6E6FA', outline='#D8BFD8', width=1
        )
        
        # Right wing
        right_wing_points = [
            draw_x + 40, draw_y - 12 - wing_offset,
            draw_x + 50, draw_y - 22,
            draw_x + 42, draw_y + 2,
            draw_x + 32, draw_y - 4
        ]
        self.canvas.create_polygon(
            right_wing_points, fill='#E6E6FA', outline='#D8BFD8', width=1
        )
        
        # Draw a glowing aura around the fairy
        aura_size = self.orb_radius + 5
        self.canvas.create_oval(
            draw_x - aura_size, 
            draw_y - aura_size, 
            draw_x + aura_size, 
            draw_y + aura_size,
            outline='#9370DB', width=1, stipple='gray50'
        )
    
    def animate(self):
        """Enhanced animation with more visual elements"""
        # Handle blinking
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            if random.randint(0, 60) == 0:
                self.blink_state = False
                self.blink_timer = 10
        
        # Simple wing animation
        self.wing_phase += 0.15
        
        # Simple bounce
        self.bounce_offset = math.sin(time.time() * 2) * 1.5
        
        # Add sparkles at a higher rate
        if random.randint(0, 10) == 0:  # More frequent sparkles
            # Position sparkles around the fairy
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(30, 70)
            sparkle_x = 90 + distance * math.cos(angle)
            sparkle_y = 90 + self.bounce_offset + distance * math.sin(angle)
            
            # Random sparkle type
            sparkle_types = ["star", "heart", "circle"]
            s_type = random.choice(sparkle_types)
            
            self.sparkles.append((sparkle_x, sparkle_y, 0, s_type))
        
        # Add occasional "magic" particles
        if random.randint(0, 30) == 0:
            # Position particles near the fairy
            particle_x = 90 + random.randint(-40, 40)
            particle_y = 90 + self.bounce_offset + random.randint(-40, 40)
            self.sparkles.append((particle_x, particle_y, 0, "circle"))
        
        # Simple orbit (for testing)
        self.orbit_angle += 0.003
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        new_x = self.center_x + self.orbit_radius * math.cos(self.orbit_angle) - 90
        new_y = self.center_y + self.orbit_radius * 0.5 * math.sin(self.orbit_angle) - 90
        
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
        self.root.geometry(f"180x180+{self.x}+{self.y}")
    
    def on_drag_stop(self, event):
        """Stop dragging the fairy"""
        pass
    
    def run(self):
        """Start the fairy system"""
        self.root.mainloop()


def main():
    print("Starting Enhanced Sparkle MIST Fairy...")
    print("This version has more visual elements and sparkles at higher rate.")
    print("Positioned in center of screen for visibility.")
    
    fairy = EnhancedSparkleFairy()
    fairy.run()


if __name__ == "__main__":
    main()