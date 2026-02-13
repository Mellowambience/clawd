"""
Enhanced Aware Companion Fairy Orb
- Even smaller body with bigger wings
- Additional interactive functions
"""

import tkinter as tk
import math
import time
import random
from PIL import Image, ImageDraw
import json
import os


class EnhancedCompanion:
    def __init__(self):
        # Create a transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("Enhanced Aware Companion Fairy")
        
        # Set transparency and attributes
        self.root.configure(bg='white')
        self.root.attributes('-transparentcolor', 'white')  # Make white transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations
        
        # Size the window appropriately for the fairy
        self.root.geometry("180x180")  # Smaller window for smaller fairy
        
        # Position fairy initially in upper right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - 200  # Adjusted for smaller fairy
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
        self.orb_radius = 35  # Even smaller body
        self.eye_size = 7     # Smaller eyes to match
        self.mouth_width = 8  # Smaller mouth
        self.mouth_height = 4
        
        # Color palette
        self.orb_color = '#F0E6FF'  # Soft lavender-white
        self.eye_color = '#6B8E23'  # Olive green (quiet awareness)
        self.mouth_color = '#FADADD'  # Light pink (minimal mouth)
        self.wing_color = '#E6E6FA'  # Light lavender (organic wings)
        self.cheek_color = '#FFD1DC'  # Light pink (rosy cheeks)
        self.party_hat_color = '#FFD700'  # Gold (party hat)
        
        # Animation and behavior properties
        self.blink_state = True
        self.blink_timer = 0
        self.head_tilt = 0
        self.wing_flap = 0
        self.wing_flap_direction = 1
        self.visible = True
        self.expression_state = "neutral"  # neutral, happy, thoughtful, surprised
        
        # Mouse following properties
        self.target_x = self.x + 90  # Center of fairy
        self.target_y = self.y + 90  # Center of fairy
        self.follow_speed = 0.01  # Very slow following speed
        
        # Additional functions
        self.function_mode = "aware"  # aware, notification, timer, weather, mood
        self.notification_text = ""
        self.notification_timer = 0
        self.timer_remaining = 0
        self.timer_active = False
        self.mood_level = 5  # 1-10 scale
        
        # Interaction states
        self.interaction_state = "aware"
        
        # Track mouse position continuously
        self.track_mouse()
        
        # Draw initial fairy
        self.draw_fairy()
        
        # Start animation
        self.animate()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
        
        # Bind double-click to cycle interaction states
        self.canvas.bind("<Double-Button-1>", self.cycle_interaction_state)
        
        # Bind right-click to cycle functions
        self.canvas.bind("<Button-3>", self.cycle_function_mode)
        
        # Bind scroll wheel for mood adjustment
        self.canvas.bind("<MouseWheel>", self.adjust_mood)
    
    def track_mouse(self):
        """Continuously track mouse position"""
        try:
            # Get mouse position relative to screen
            mouse_x = self.root.winfo_pointerx()
            mouse_y = self.root.winfo_pointery()
            
            # Set as target position (with some offset to aim for the center)
            self.target_x = mouse_x
            self.target_y = mouse_y
        except:
            # If mouse tracking fails, continue with current target
            pass
        
        # Schedule next mouse tracking
        self.root.after(50, self.track_mouse)  # Update every 50ms
    
    def draw_fairy(self):
        """Draw the fairy with enhanced features"""
        self.canvas.delete("all")
        
        if not self.visible:
            return
        
        # Calculate position for smooth following
        current_center_x = self.x + 90  # Adjusted for smaller canvas
        current_center_y = self.y + 90  # Adjusted for smaller canvas
        
        # Calculate distance to target
        dx = self.target_x - current_center_x
        dy = self.target_y - current_center_y
        
        # Move gradually toward target (slow following)
        move_x = dx * self.follow_speed
        move_y = dy * self.follow_speed
        
        # Calculate new position (with boundaries to prevent going off-screen)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        new_center_x = max(90, min(screen_width - 90, current_center_x + move_x))
        new_center_y = max(90, min(screen_height - 90, current_center_y + move_y))
        
        # Calculate offset from original position
        offset_x = new_center_x - (self.x + 90)
        offset_y = new_center_y - (self.y + 90)
        
        # Update position
        self.x = int(new_center_x - 90)
        self.y = int(new_center_y - 90)
        self.root.geometry(f"180x180+{self.x}+{self.y}")
        
        # Draw the orb body (round, softly imperfect)
        center_x, center_y = 90, 90  # Centered in smaller canvas
        draw_x, draw_y = center_x + offset_x, center_y + offset_y
        
        # Draw the orb body (soft lavender-white)
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
        
        # Draw expressive green eyes (quiet awareness) - adjusted for smaller face
        left_eye_x = draw_x - 15  # Closer together for smaller face
        right_eye_x = draw_x + 15
        eye_y = draw_y - 5
        
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
        
        # Draw mouth based on expression state
        mouth_y = draw_y + 15  # Adjusted for smaller face
        if self.expression_state == "happy":
            # Happy smile
            self.canvas.create_arc(
                draw_x - self.mouth_width//2, 
                mouth_y - self.mouth_height//2,
                draw_x + self.mouth_width//2, 
                mouth_y + self.mouth_height//2,
                start=190, extent=160, style=tk.ARC, 
                outline=self.mouth_color, width=1
            )
        elif self.expression_state == "thoughtful":
            # Straight line
            self.canvas.create_line(
                draw_x - self.mouth_width//2, mouth_y,
                draw_x + self.mouth_width//2, mouth_y,
                fill=self.mouth_color, width=1
            )
        elif self.expression_state == "surprised":
            # Small circle
            self.canvas.create_oval(
                draw_x - 2, mouth_y - 2,
                draw_x + 2, mouth_y + 2,
                fill='', outline=self.mouth_color, width=1
            )
        else:
            # Neutral expression
            self.canvas.create_arc(
                draw_x - self.mouth_width//2, 
                mouth_y - self.mouth_height//4,
                draw_x + self.mouth_width//2, 
                mouth_y + self.mouth_height//4,
                start=10, extent=-160, style=tk.ARC, 
                fill='', outline=self.mouth_color, width=1
            )
        
        # Draw organic wings (light lavender, semi-translucent) - bigger wings for smaller body
        wing_offset = math.sin(time.time() * 2) * 2  # Gentle wing movement
        
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
        hat_x = draw_x + 3  # Even smaller adjustment
        hat_y = draw_y - 15 + self.head_tilt * 1.5  # Hat tilts with head, smaller
        hat_points = [
            hat_x, hat_y - 8,  # Tip of hat, smaller
            hat_x - 5, hat_y - 2,  # Left base
            hat_x + 5, hat_y - 2,  # Right base
        ]
        self.canvas.create_polygon(
            hat_points, fill=self.party_hat_color, outline='#D4AF37', width=1
        )
        
        # Draw hat decoration - smaller
        self.canvas.create_oval(
            hat_x - 1, hat_y - 6, hat_x + 1, hat_y - 4,
            fill='#FF69B4', outline=''
        )
        
        # Draw notification indicator if active
        if self.function_mode == "notification" and self.notification_text:
            # Draw a small notification badge
            self.canvas.create_oval(
                draw_x + 30, draw_y - 30,
                draw_x + 40, draw_y - 20,
                fill='#FF69B4', outline='#D4AF37', width=1
            )
            self.canvas.create_text(
                draw_x + 35, draw_y - 25,
                text="!", fill='white', font=('Arial', 8, 'bold')
            )
        
        # Draw timer indicator if active
        if self.function_mode == "timer" and self.timer_active:
            # Draw a small clock indicator
            self.canvas.create_oval(
                draw_x + 30, draw_y - 10,
                draw_x + 40, draw_y,
                fill='#6B8E23', outline='#4A6B1F', width=1
            )
            self.canvas.create_line(
                draw_x + 35, draw_y - 5,
                draw_x + 35, draw_y - 2,
                fill='white', width=1
            )
            self.canvas.create_line(
                draw_x + 35, draw_y - 5,
                draw_x + 37, draw_y - 5,
                fill='white', width=1
            )
    
    def animate(self):
        """Animate the fairy with enhanced features"""
        # Handle blinking (more frequent now)
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            # Increase blink frequency - blink more often
            if random.randint(0, 60) == 0:  # Blink approximately every 1-2 seconds
                self.blink_state = False
                self.blink_timer = 15  # Blink for 15 frames (shorter blink)
        
        # Very occasional head tilt
        if random.randint(0, 300) == 0:  # Rare head tilt
            self.head_tilt = random.choice([-1, 1])
            # Reset after a while
            self.root.after(600, self.reset_head_tilt)
        
        # Update notification timer if active
        if self.notification_timer > 0:
            self.notification_timer -= 1
            if self.notification_timer <= 0:
                self.notification_text = ""
        
        # Update timer if active
        if self.timer_active and self.timer_remaining > 0:
            self.timer_remaining -= 0.03  # Approximate time per frame
            if self.timer_remaining <= 0:
                self.timer_active = False
                self.show_notification("Timer finished!")
        
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
        
        # Update target position when dragged
        self.target_x = new_x + 90
        self.target_y = new_y + 90
    
    def on_drag_stop(self, event):
        """Stop dragging the fairy"""
        pass
    
    def cycle_interaction_state(self, event):
        """Cycle through different interaction states"""
        states = ["aware", "listening", "responding", "waiting"]
        current_index = states.index(self.interaction_state)
        next_index = (current_index + 1) % len(states)
        self.interaction_state = states[next_index]
        print(f"Interaction state: {self.interaction_state}")
    
    def cycle_function_mode(self, event):
        """Cycle through different function modes"""
        modes = ["aware", "notification", "timer", "mood"]
        current_index = modes.index(self.function_mode)
        next_index = (current_index + 1) % len(modes)
        self.function_mode = next_index
        print(f"Function mode: {self.function_mode}")
    
    def adjust_mood(self, event):
        """Adjust mood level with mouse wheel"""
        if event.delta > 0:
            self.mood_level = min(10, self.mood_level + 1)
        else:
            self.mood_level = max(1, self.mood_level - 1)
        
        # Change expression based on mood
        if self.mood_level >= 8:
            self.expression_state = "happy"
        elif self.mood_level >= 6:
            self.expression_state = "neutral"
        elif self.mood_level >= 4:
            self.expression_state = "thoughtful"
        else:
            self.expression_state = "surprised"
        
        print(f"Mood level: {self.mood_level}/10")
    
    def set_interaction_state(self, state, duration=300):  # Duration in animation frames
        """Set the interaction state of the fairy"""
        self.interaction_state = state
    
    def show_notification(self, text, duration=300):  # Duration in frames
        """Show a notification"""
        self.notification_text = text
        self.notification_timer = duration
        self.function_mode = "notification"
    
    def start_timer(self, seconds):
        """Start a timer"""
        self.timer_remaining = seconds
        self.timer_active = True
        self.function_mode = "timer"
    
    def appear(self):
        """Make the fairy appear"""
        self.set_interaction_state("responding", 200)
        # Visual indication only
        pass
    
    def listen_mode(self):
        """Set fairy to listening mode"""
        self.set_interaction_state("listening", 600)
    
    def respond_mode(self):
        """Set fairy to responding mode"""
        self.set_interaction_state("responding", 300)
    
    def wait_mode(self):
        """Set fairy to waiting mode"""
        self.set_interaction_state("waiting", 1000)
    
    def aware_mode(self):
        """Set fairy to aware mode"""
        self.set_interaction_state("aware", 0)
    
    def disappear(self):
        """Make the fairy gently disappear"""
        self.visible = False
        self.canvas.delete("all")
    
    def run(self):
        """Start the fairy system"""
        self.root.mainloop()


def main():
    print("Starting Enhanced Aware Companion Fairy...")
    print("Changes include:")
    print("- Even smaller body (radius 35)")
    print("- Bigger wings for more dramatic effect")
    print("- Additional functions: notification, timer, mood tracking")
    print("- Right-click to cycle through function modes")
    print("- Mouse wheel to adjust mood level")
    print("- All other features preserved")
    
    companion = EnhancedCompanion()
    
    # Example: Make companion appear
    def demo_appear():
        companion.appear()
    
    # Schedule demo appearance after 2 seconds
    companion.root.after(2000, demo_appear)
    
    # Example: Show a notification after 5 seconds
    def demo_notification():
        companion.show_notification("Hello, sister!")
    
    companion.root.after(5000, demo_notification)
    
    companion.run()


if __name__ == "__main__":
    main()