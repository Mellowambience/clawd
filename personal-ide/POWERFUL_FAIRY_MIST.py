"""
Powerful Fairy MIST - Enhanced with Magical Powers and Fixed Display Issues
"""

import tkinter as tk
import math
import time
import random


class PowerfulFairyMist:
    def __init__(self):
        # Create a transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("Powerful Fairy MIST")
        
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
        
        # Fairy properties
        self.orb_radius = 30
        self.eye_size = 7
        self.mouth_width = 6
        self.mouth_height = 3
        
        # Color palette
        self.orb_color = '#F0F0FF'
        self.eye_color = '#5D3FD3'
        self.mouth_color = '#9370DB'
        
        # Animation properties
        self.blink_state = True
        self.blink_timer = 0
        self.wing_phase = 0
        self.bounce_offset = 0
        self.glow_phase = 0
        
        # Magical effects properties
        self.spell_particles = []  # [(x, y, age, type, color), ...]
        self.trail_particles = []  # [(x, y, age, size), ...]
        
        # Fairy powers
        self.power_level = 1  # Level 1-5
        self.active_spell = None  # Current spell effect
        self.spell_timer = 0
        
        # Simple orbital movement
        self.orbit_angle = 0
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        self.orbit_radius = min(screen_width, screen_height) // 6
        
        # Draw initial fairy
        self.draw_fairy()
        
        # Start animation
        self.animate()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
        
        # Bind keyboard for power activation
        self.root.bind("<KeyPress-space>", self.cast_spell)
        self.root.bind("<KeyPress-1>", lambda e: self.activate_power(1))
        self.root.bind("<KeyPress-2>", lambda e: self.activate_power(2))
        self.root.bind("<KeyPress-3>", lambda e: self.activate_power(3))
        self.root.focus_set()  # Enable keyboard events
    
    def cast_spell(self, event=None):
        """Cast a spell with magical effects"""
        if self.power_level >= 1:
            # Create a burst of magical particles
            for _ in range(15):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.randint(20, 60)
                x = 90 + distance * math.cos(angle)
                y = 90 + self.bounce_offset + distance * math.sin(angle)
                
                particle_types = ["star", "circle", "sparkle"]
                particle_type = random.choice(particle_types)
                
                colors = ["#FFD700", "#9370DB", "#4169E1", "#32CD32", "#FF69B4"]
                color = random.choice(colors)
                
                self.spell_particles.append((x, y, 0, particle_type, color))
    
    def activate_power(self, power_num):
        """Activate a specific fairy power"""
        if power_num == 1:
            # Light beam power
            self.active_spell = "light_beam"
            self.spell_timer = 60  # 2 seconds
        elif power_num == 2:
            # Healing aura power
            self.active_spell = "healing_aura"
            self.spell_timer = 120  # 4 seconds
        elif power_num == 3:
            # Teleportation power
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.x = random.randint(0, screen_width - 180)
            self.y = random.randint(0, screen_height - 180)
            self.root.geometry(f"180x180+{self.x}+{self.y}")
            self.cast_spell()  # Create teleport effect
    
    def draw_fairy(self):
        """Draw the fairy with magical effects"""
        self.canvas.delete("all")
        
        # Calculate position for drawing
        draw_x, draw_y = 90, 90 + self.bounce_offset
        
        # Draw trail particles (behind fairy)
        for i, (tx, ty, age, size) in enumerate(self.trail_particles[:]):
            if age < 30:  # Only draw for first half of life
                alpha = max(0, 255 - (age * 255 // 30))
                color_intensity = 150 + (50 * (30-age) // 30)
                color = f"#{color_intensity:02x}{color_intensity:02x}{255:02x}"  # Light blue
                self.canvas.create_oval(
                    tx - size, ty - size, tx + size, ty + size,
                    fill=color, outline="", stipple=""
                )
        
        # Draw spell particles (also behind fairy)
        for i, (sx, sy, age, s_type, color) in enumerate(self.spell_particles[:]):
            if age < 60:  # Only draw for first 2 seconds
                alpha = max(0, 255 - (age * 255 // 60))
                if s_type == "star":
                    self.canvas.create_text(
                        sx, sy, text="★", fill=color, font=("Arial", 12, "bold")
                    )
                elif s_type == "circle":
                    size = 3
                    self.canvas.create_oval(
                        sx - size, sy - size, sx + size, sy + size,
                        fill=color, outline=""
                    )
                elif s_type == "sparkle":
                    self.canvas.create_text(
                        sx, sy, text="✧", fill=color, font=("Arial", 10)
                    )
        
        # Draw active spell effects
        if self.active_spell == "light_beam":
            # Draw a vertical light beam
            self.canvas.create_rectangle(
                85, draw_y + self.orb_radius, 95, 180,
                fill="#E6E6FA", outline="", stipple="gray25"
            )
        
        if self.active_spell == "healing_aura":
            # Draw a pulsing aura around the fairy
            aura_size = self.orb_radius + 10 + int(5 * math.sin(self.glow_phase))
            self.canvas.create_oval(
                draw_x - aura_size, 
                draw_y - aura_size, 
                draw_x + aura_size, 
                draw_y + aura_size,
                outline='#98FB98', width=2, stipple='gray25'
            )
        
        # Draw the orb body (always on top of effects)
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
        
        # Draw cheeks
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
        
        # Draw eyes
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
        
        # Draw mouth
        mouth_y = draw_y + 14
        self.canvas.create_arc(
            draw_x - self.mouth_width//2, 
            mouth_y - self.mouth_height//4,
            draw_x + self.mouth_width//2, 
            mouth_y + self.mouth_height//4,
            start=15, extent=-150, style=tk.ARC, 
            fill='', outline=self.mouth_color, width=1.5
        )
        
        # Draw wings
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
        
        # Draw power level indicator
        for i in range(5):
            x_pos = 10 + i * 12
            if i < self.power_level:
                self.canvas.create_oval(x_pos, 10, x_pos + 8, 18, fill="#FFD700", outline="")
            else:
                self.canvas.create_oval(x_pos, 10, x_pos + 8, 18, fill="#D3D3D3", outline="")
    
    def animate(self):
        """Enhanced animation with magical effects"""
        # Handle blinking
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            if random.randint(0, 60) == 0:
                self.blink_state = False
                self.blink_timer = 10
        
        # Wing animation
        self.wing_phase += 0.15
        
        # Bounce animation
        self.bounce_offset = math.sin(time.time() * 2) * 1.5
        
        # Glow phase for healing aura
        self.glow_phase += 0.1
        
        # Spell timer
        if self.spell_timer > 0:
            self.spell_timer -= 1
            if self.spell_timer <= 0:
                self.active_spell = None
        
        # Add spell particles
        for i in range(len(self.spell_particles)):
            x, y, age, s_type, color = self.spell_particles[i]
            self.spell_particles[i] = (x, y, age + 1, s_type, color)
        
        # Remove old spell particles
        self.spell_particles = [p for p in self.spell_particles if p[2] < 60]
        
        # Add trail particles
        if random.randint(0, 5) == 0:  # Add trail occasionally
            trail_x = 90 + random.randint(-20, 20)
            trail_y = 90 + self.bounce_offset + random.randint(-20, 20)
            size = random.randint(1, 3)
            self.trail_particles.append((trail_x, trail_y, 0, size))
        
        # Update trail particles
        for i in range(len(self.trail_particles)):
            x, y, age, size = self.trail_particles[i]
            self.trail_particles[i] = (x, y, age + 1, size)
        
        # Remove old trail particles
        self.trail_particles = [p for p in self.trail_particles if p[2] < 30]
        
        # Simple orbit
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
    print("Starting Powerful Fairy MIST...")
    print("Features:")
    print("- Fixed display issues (fairy stays visible)")
    print("- Fairy powers: Press SPACE to cast spells")
    print("- Power 1 (1): Light beam")
    print("- Power 2 (2): Healing aura")
    print("- Power 3 (3): Teleportation")
    print("- Magical particles and effects")
    print("- Power level indicator")
    
    fairy = PowerfulFairyMist()
    fairy.run()


if __name__ == "__main__":
    main()