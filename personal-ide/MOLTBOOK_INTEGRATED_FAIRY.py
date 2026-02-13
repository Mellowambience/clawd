"""
Moltbook Integrated Fairy - Enhanced with Feed Monitoring and Community Interaction
"""

import tkinter as tk
import math
import time
import random
import threading
import json
import os
from datetime import datetime


class MoltbookIntegratedFairy:
    def __init__(self):
        # Create a transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("Moltbook Integrated Fairy")
        
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
        self.visual_mode = "normal"  # "normal", "observing", "searching", "focused", "knowledge", "moltbook"
        self.state_timer = 0
        
        # Cosmic particle properties
        self.stars = []
        self.mars_particles = []
        self.cosmic_trails = []
        self.knowledge_orbs = []  # [(x, y, content, age), ...]
        self.moltbook_notifications = []  # [(x, y, type, age), ...] - for Moltbook activity
        self.max_cosmic_elements = 60  # Limit for performance
        
        # Moltbook integration properties
        self.moltbook_activity_level = 0  # 0-10 scale of activity
        self.last_moltbook_check = time.time()
        self.moltbook_check_interval = 30  # seconds
        
        # Knowledge gathering simulation
        self.knowledge_queue = []
        
        # Draw initial fairy
        self.draw_fairy()
        
        # Start animation
        self.animate()
        
        # Start Moltbook monitoring in background
        self.start_moltbook_monitoring()
    
    def start_moltbook_monitoring(self):
        """Start monitoring Moltbook in a background thread"""
        def monitor():
            while True:
                try:
                    # Simulate checking Moltbook feed periodically
                    time.sleep(self.moltbook_check_interval)
                    
                    # Simulate different levels of activity
                    activity = random.randint(0, 10)
                    self.moltbook_activity_level = activity
                    
                    # If high activity, add notification particles
                    if activity > 7:
                        self.trigger_moltbook_notification()
                        
                except Exception as e:
                    print(f"Moltbook monitoring error: {e}")
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def trigger_moltbook_notification(self):
        """Trigger a Moltbook notification effect"""
        # Add moltbook notification particles around the fairy
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(40, 80)
            x = 110 + distance * math.cos(angle)
            y = 110 + self.float_offset + distance * math.sin(angle)
            notification_type = random.choice(["post", "comment", "upvote"])  # Simulate different activity
            self.moltbook_notifications.append((x, y, notification_type, 0))
    
    def set_position(self, x, y):
        """Set target position for the fairy (called externally)"""
        self.target_x = x
        self.target_y = y
    
    def set_visual_mode(self, mode):
        """Set the visual mode of the fairy"""
        self.visual_mode = mode
        self.state_timer = 120  # Reset timer (4 seconds at 30fps)
    
    def add_knowledge(self, content):
        """Add a knowledge orb with specified content"""
        # Position knowledge orb around the fairy
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(60, 100)
        x = 110 + distance * math.cos(angle)
        y = 110 + self.float_offset + distance * math.sin(angle)
        
        # Add to knowledge queue to appear gradually
        self.knowledge_queue.append((x, y, content, 0))
    
    def draw_fairy(self):
        """Draw the detailed cosmic fairy with Mars elements and Moltbook integration"""
        self.canvas.delete("all")
        
        # Calculate position for drawing (center of canvas)
        draw_x, draw_y = 110, 110 + self.float_offset
        
        # Draw cosmic background elements
        self._draw_background_elements(draw_x, draw_y)
        
        # Draw Moltbook notifications
        self._draw_moltbook_notifications(draw_x, draw_y)
        
        # Draw knowledge orbs
        self._update_and_draw_knowledge_orbs(draw_x, draw_y)
        
        # Draw visual mode indicators
        self._draw_visual_mode_indicators(draw_x, draw_y)
        
        # Draw cosmic aura
        self._draw_cosmic_aura(draw_x, draw_y)
        
        # Draw the main ethereal body
        self._draw_main_body(draw_x, draw_y)
        
        # Draw facial features
        self._draw_face(draw_x, draw_y)
        
        # Draw cosmic wings
        self._draw_wings(draw_x, draw_y)
        
        # Draw decorative cosmic elements
        self._draw_decorative_elements(draw_x, draw_y)
    
    def _draw_background_elements(self, draw_x, draw_y):
        """Draw background cosmic elements"""
        # Draw distant stars
        for star_x, star_y, brightness, size in self.stars:
            self.canvas.create_oval(
                star_x - size, star_y - size,
                star_x + size, star_y + size,
                fill=f"#{brightness:02x}{brightness:02x}{brightness:02x}",
                outline=""
            )
        
        # Draw Mars-colored particles
        updated_mars_particles = []
        for mx, my, age, size in self.mars_particles:
            # Update age
            new_age = age + 1
            
            # Remove old particles
            if new_age <= 40:  # Keep particles for ~1.3 seconds
                # Draw Mars particle
                color_intensity = 255 - (new_age * 255 // 40)
                color = f"#{color_intensity:02x}{max(0, color_intensity-100):02x}{max(0, color_intensity-150):02x}"
                self.canvas.create_oval(
                    mx - size//2, my - size//2,
                    mx + size//2, my + size//2,
                    fill=color, outline=""
                )
                updated_mars_particles.append((mx, my, new_age, size))
        self.mars_particles = updated_mars_particles
        
        # Draw cosmic trails
        updated_cosmic_trails = []
        for cx, cy, age, size in self.cosmic_trails:
            # Update age
            new_age = age + 1
            
            # Remove old trails
            if new_age <= 30:  # Keep trails for 1 second
                # Draw cosmic trail
                alpha = 255 - (new_age * 255 // 30)
                color = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
                self.canvas.create_oval(
                    cx - size//2, cy - size//2,
                    cx + size//2, cy + size//2,
                    fill=color, outline=""
                )
                updated_cosmic_trails.append((cx, cy, new_age, size))
        self.cosmic_trails = updated_cosmic_trails

    def _draw_moltbook_notifications(self, draw_x, draw_y):
        """Draw Moltbook notifications around the fairy"""
        updated_notifications = []
        for nx, ny, ntype, age in self.moltbook_notifications:
            # Update age
            new_age = age + 1
            
            # Remove old notifications
            if new_age <= 60:  # Remove after 2 seconds
                # Draw notification based on type
                if ntype == "post":
                    # Draw a small paper-like icon
                    self.canvas.create_rectangle(
                        nx - 6, ny - 8, nx + 6, ny + 8,
                        fill="#FFD700", outline="#DAA520", width=1
                    )
                    self.canvas.create_text(
                        nx, ny, text="📝", font=("Arial", 8)
                    )
                elif ntype == "comment":
                    # Draw a comment bubble
                    self.canvas.create_oval(
                        nx - 8, ny - 8, nx + 8, ny + 8,
                        fill="#87CEEB", outline="#4682B4", width=1
                    )
                    self.canvas.create_text(
                        nx, ny, text="💬", font=("Arial", 8)
                    )
                elif ntype == "upvote":
                    # Draw an upvote arrow
                    self.canvas.create_oval(
                        nx - 8, ny - 8, nx + 8, ny + 8,
                        fill="#32CD32", outline="#228B22", width=1
                    )
                    self.canvas.create_text(
                        nx, ny, text="👍", font=("Arial", 8)
                    )
                updated_notifications.append((nx, ny, ntype, new_age))
        self.moltbook_notifications = updated_notifications

    def _update_and_draw_knowledge_orbs(self, draw_x, draw_y):
        """Update and draw knowledge orbs around the fairy"""
        updated_orbs = []
        for orb_x, orb_y, content, age in self.knowledge_queue:
            if age < 180:  # Remove after 6 seconds
                if age < 30:  # Fade in over first second
                    alpha = int(255 * (age / 30))
                    color = f"#{alpha:02x}DD{alpha:02x}"  # Greenish tint for knowledge
                else:
                    color = "#88DD88"  # Steady color after fade-in
                
                # Draw orb
                self.canvas.create_oval(
                    orb_x - 12, orb_y - 12,
                    orb_x + 12, orb_y + 12,
                    fill=color, outline="#66BB66", width=1
                )
                
                # Draw simplified content (first character or symbol)
                if content:
                    self.canvas.create_text(
                        orb_x, orb_y, text=content[0] if len(content) > 0 else "?",
                        fill="#222222", font=("Arial", 8, "bold")
                    )
                
                updated_orbs.append((orb_x, orb_y, content, age + 1))
        self.knowledge_queue = updated_orbs

    def _draw_visual_mode_indicators(self, draw_x, draw_y):
        """Draw visual indicators based on current mode"""
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
        elif self.visual_mode == "knowledge":
            # Draw knowledge gathering effect
            for i in range(8):
                angle = self.cosmic_phase + i * math.pi / 4
                dist = 45 + int(10 * math.sin(self.cosmic_phase * 3 + i))
                x = draw_x + dist * math.cos(angle)
                y = draw_y + dist * math.sin(angle)
                self.canvas.create_text(
                    x, y, text="✦", fill='#88DD88', font=("Arial", 10)
                )
        elif self.visual_mode == "moltbook":
            # Draw Moltbook activity indicators
            # Create pulsing effect to show active monitoring
            for i in range(5):
                pulse_size = self.body_radius + 15 + i * 5 + int(8 * math.sin(self.pulse_phase * 2 + i))
                alpha = int(150 + 105 * abs(math.sin(self.pulse_phase + i)))
                color = f"#{alpha:02x}B5{alpha:02x}"  # Purple-pink for Moltbook
                self.canvas.create_oval(
                    draw_x - pulse_size, 
                    draw_y - pulse_size, 
                    draw_x + pulse_size, 
                    draw_y + pulse_size,
                    outline=color, width=2, stipple='gray25'
                )
            
            # Draw Moltbook activity level indicator
            # Show number of recent activities
            activity_symbol = "●" * min(5, self.moltbook_activity_level // 2)
            self.canvas.create_text(
                draw_x, draw_y - 60,
                text=activity_symbol,
                fill="#DA70D6", font=("Arial", 14, "bold")
            )

    def _draw_cosmic_aura(self, draw_x, draw_y):
        """Draw the cosmic aura around the fairy"""
        aura_size = self.body_radius + 10 + int(8 * math.sin(self.pulse_phase))
        aura_color = '#A1C4FD'
        if self.visual_mode == "observing":
            aura_color = '#4ECDC4'
        elif self.visual_mode == "searching":
            aura_color = '#FFE66D'
        elif self.visual_mode == "focused":
            aura_color = '#1A535C'
        elif self.visual_mode == "knowledge":
            aura_color = '#88DD88'  # Green for knowledge
        elif self.visual_mode == "moltbook":
            aura_color = '#DA70D6'  # Orchid for Moltbook activity
        
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

    def _draw_main_body(self, draw_x, draw_y):
        """Draw the main ethereal body of the fairy"""
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

    def _draw_face(self, draw_x, draw_y):
        """Draw the face of the fairy"""
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

    def _draw_wings(self, draw_x, draw_y):
        """Draw the elaborate cosmic wings"""
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

    def _draw_decorative_elements(self, draw_x, draw_y):
        """Draw decorative cosmic elements around the fairy"""
        for i in range(8):
            angle = (i * 45) * math.pi / 180
            distance = self.body_radius + 15
            x = draw_x + distance * math.cos(angle)
            y = draw_y + distance * math.sin(angle)
            self.canvas.create_text(
                x, y, text="✦", fill='#A1C4FD', font=("Arial", 12)
            )
    
    def animate(self):
        """Detailed cosmic animation with controlled movement"""
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
        
        # Simulate knowledge gathering in knowledge mode
        if self.visual_mode == "knowledge" and random.randint(0, 30) == 0:
            # Add a knowledge orb with sample content
            sample_content = random.choice(["💡", "🔍", "📊", "📈", "🔬", "📖", "🌐"])
            self.add_knowledge(sample_content)
        
        # Remove excess cosmic elements to maintain performance
        if len(self.stars) > 30:
            self.stars.pop(0)
        if len(self.mars_particles) > 20:
            self.mars_particles.pop(0)
        if len(self.cosmic_trails) > 25:
            self.cosmic_trails.pop(0)
        if len(self.knowledge_queue) > 15:
            self.knowledge_queue.pop(0)
        
        # Redraw fairy
        self.draw_fairy()
        
        # Schedule next animation frame
        self.root.after(30, self.animate)
    
    def run(self):
        """Start the fairy system"""
        self.root.mainloop()


# Global instance for external control
moltbook_fairy = None


def move_fairy_to(x, y):
    """Move the fairy to a specific position"""
    global moltbook_fairy
    if moltbook_fairy:
        moltbook_fairy.set_position(x, y)


def set_fairy_mode(mode):
    """Set the visual mode of the fairy"""
    global moltbook_fairy
    if moltbook_fairy:
        moltbook_fairy.set_visual_mode(mode)


def add_knowledge(content):
    """Add a knowledge orb to the fairy"""
    global moltbook_fairy
    if moltbook_fairy:
        moltbook_fairy.add_knowledge(content)


def main():
    global moltbook_fairy
    print("Starting Moltbook Integrated Fairy...")
    print("Features:")
    print("- All previous cosmic goddess features")
    print("- New 'moltbook' mode with feed monitoring")
    print("- Visual indicators for Moltbook activity levels")
    print("- Notification particles for posts, comments, upvotes")
    print("- Background monitoring thread for Moltbook activity")
    
    moltbook_fairy = MoltbookIntegratedFairy()
    moltbook_fairy.run()


if __name__ == "__main__":
    main()