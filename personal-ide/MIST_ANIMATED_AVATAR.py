"""
MIST Animated Avatar System
Comprehensive animated fairy avatar with multiple animation sets
"""

import tkinter as tk
import math
import time
import threading
import winsound
from datetime import datetime
import random


# Gentle, girly sound patterns for the fairy
FAIRY_SOUND_PATTERNS = {
    'a': (659, 80),    # E note - soft and pleasant
    'e': (784, 80),    # G note - bright and cheerful  
    'i': (880, 80),    # A note - light and airy
    'o': (740, 80),    # F note - warm and round
    'u': (988, 80),    # B note - sweet and high
    ' ': (0, 100),     # Brief silence
    '.': (523, 60),    # C note - gentle ending
    ',': (587, 50),    # D note - light pause
    '!': (1047, 70),   # High C - cheerful emphasis
    '?': (932, 70),    # A# note - questioning tone
    'g': (831, 80),    # G# note - for "girlie" sounds
    'l': (740, 80),    # F note - for "girly" sounds
    'r': (698, 80),    # F note - for "girly" sounds
    'y': (880, 80),    # A note - for "girly" sounds
}

def play_girly_sound(text):
    """
    Play gentle, girly sounds for the fairy
    """
    text = text.lower()
    for char in text:
        if char in FAIRY_SOUND_PATTERNS:
            freq, duration = FAIRY_SOUND_PATTERNS[char]
            if freq > 0:  # Only beep if frequency is not zero (for spaces)
                try:
                    winsound.Beep(freq, duration)
                except:
                    # Beep might not work on all systems, just continue
                    pass
            time.sleep(duration/1000.0)
        else:
            # Use a default pleasant note for other characters
            try:
                winsound.Beep(784, 60)  # G note - pleasant default
            except:
                pass
            time.sleep(0.06)

def play_short_girly_sound():
    """
    Play a short, pleasant girly sound sequence
    """
    # Play a short melodic sequence: G-E-G-C
    sequence = [(784, 60), (659, 60), (784, 60), (523, 100)]  # G-E-G-C
    for freq, duration in sequence:
        try:
            winsound.Beep(freq, duration)
        except:
            pass
        time.sleep(duration/1000.0)

def play_girly_response(text):
    """
    Play a pleasant response with girly tones
    """
    thread = threading.Thread(target=play_girly_sound, args=(text,))
    thread.daemon = True
    thread.start()

def play_girly_ping():
    """
    Play a short, pleasant ping sound
    """
    thread = threading.Thread(target=play_short_girly_sound)
    thread.daemon = True
    thread.start()


class MISTAnimatedAvatar:
    def __init__(self):
        # Create a transparent window for the avatar
        self.root = tk.Tk()
        self.root.title("MIST Animated Avatar")
        
        # Set transparency and attributes
        self.root.configure(bg='white')
        self.root.attributes('-transparentcolor', 'white')  # Make white transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations
        
        # Size the window appropriately for the avatar
        self.root.geometry("200x200")
        
        # Position avatar initially in upper right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - 250
        self.y = 50
        self.root.geometry(f"200x200+{self.x}+{self.y}")
        
        # Create canvas for drawing avatar
        self.canvas = tk.Canvas(
            self.root,
            width=200,
            height=200,
            bg='white',  # This will be transparent
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Avatar properties
        self.size = 60
        self.eye_size = 12
        self.eye_offset_x = 15
        self.eye_offset_y = 10
        self.mouth_width = 20
        self.mouth_height = 10
        
        # Official MIST colors
        self.skin_color = '#FFF8DC'  # Cornsilk (lighter, warmer)
        self.eye_color = '#98FB98'   # Pale green (gentle, caring)
        self.mouth_color = '#FFB6C1' # Light pink (soft)
        self.wing_color = '#E6E6FA'  # Lavender (gentle)
        self.hair_color = '#FFE4E1'  # Misty rose (soft)
        self.glow_color = '#F0F8FF'  # Alice blue (soft)
        self.body_outline = '#F5F5DC' # Beige outline
        
        # Animation states
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.float_offset = 0
        self.blink_state = True
        self.blink_timer = 0
        self.visible = True
        self.bounce_height = 0
        self.bounce_direction = 1
        self.interaction_state = "idle"
        self.interaction_timer = 0
        self.wing_flap = 0
        self.wing_flap_direction = 1
        self.eye_blink_counter = 0
        
        # Animation sequences
        self.animations = {
            "idle": self.animate_idle,
            "listening": self.animate_listening,
            "responding": self.animate_responding,
            "happy": self.animate_happy,
            "excited": self.animate_excited,
            "thinking": self.animate_thinking,
            "sleeping": self.animate_sleeping
        }
        
        # Drag data for moving the avatar
        self.drag_data = {"x": 0, "y": 0, "start_x": 0, "start_y": 0}
        
        # Draw initial avatar
        self.draw_avatar()
        
        # Start animation
        self.animate()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
        
        # Bind double-click to reset position and cycle animation
        self.canvas.bind("<Double-Button-1>", self.cycle_animation)
    
    def draw_avatar(self):
        """Draw the animated avatar with current animation state"""
        self.canvas.delete("all")
        
        if not self.visible:
            return
            
        # Adjust colors based on interaction state
        if self.interaction_state == "listening":
            skin_col = '#FFFACD'  # Lemon chiffon
            eye_col = '#ADFF2F'   # Green yellow
        elif self.interaction_state == "responding":
            skin_col = '#FFF8DC'  # Cornsilk
            eye_col = '#98FB98'   # Pale green
        elif self.interaction_state == "happy":
            skin_col = '#FFF0F5'  # Lavender blush
            eye_col = '#AFEEEE'   # Pale turquoise
        elif self.interaction_state == "excited":
            skin_col = '#FFF8DC'  # Cornsilk
            eye_col = '#7CFC00'   # Lawn green
        elif self.interaction_state == "thinking":
            skin_col = '#FDF5E6'  # Old lace
            eye_col = '#9370DB'   # Medium purple
        elif self.interaction_state == "sleeping":
            skin_col = '#F5F5DC'  # Beige
            eye_col = '#A9A9A9'   # Dark gray
        else:
            skin_col = self.skin_color
            eye_col = self.eye_color
        
        # Apply current animation transformation
        self.animations[self.current_animation]()
        
        # Draw outer soft glow (halo effect)
        self.canvas.create_oval(
            50 + math.sin(self.float_offset) * 2, 30 + self.bounce_height, 
            150 + math.sin(self.float_offset) * 2, 130 + self.bounce_height,
            fill=self.glow_color, outline='', stipple='gray50'
        )
        
        # Draw wings with animation
        wing_flap_offset = math.sin(self.wing_flap) * 5
        
        # Left wing (animated)
        left_wing_points = [
            20, 60 + wing_flap_offset,  # Wing tip
            60, 40,  # Upper attachment
            60, 80,  # Lower attachment
        ]
        self.canvas.create_polygon(left_wing_points, fill=self.wing_color, outline='', stipple='')
        
        # Right wing (animated)
        right_wing_points = [
            180, 60 - wing_flap_offset,  # Wing tip
            140, 40,  # Upper attachment
            140, 80,  # Lower attachment
        ]
        self.canvas.create_polygon(right_wing_points, fill=self.wing_color, outline='', stipple='')
        
        # Draw main body/head with animation offset
        body_x_offset = math.sin(self.float_offset * 2) * 2
        self.canvas.create_oval(
            80 + body_x_offset, 60 + self.bounce_height, 
            120 + body_x_offset, 100 + self.bounce_height,
            fill=skin_col, outline=self.body_outline, width=2
        )
        
        # Draw hair/halo effect
        self.canvas.create_oval(
            75 + body_x_offset, 55 + self.bounce_height, 
            125 + body_x_offset, 105 + self.bounce_height,
            outline=self.hair_color, width=2, dash=(4, 4)
        )
        
        # Draw eyes
        left_eye_x = 88 + body_x_offset
        right_eye_x = 112 + body_x_offset
        eye_y = 78 + self.bounce_height
        
        if self.blink_state:
            # Draw open eyes with soft highlights
            self.canvas.create_oval(
                left_eye_x - self.eye_size, eye_y - self.eye_size,
                left_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#EEEEEE', width=1
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size, eye_y - self.eye_size,
                right_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#EEEEEE', width=1
            )
            
            # Draw soft irises
            self.canvas.create_oval(
                left_eye_x - self.eye_size*0.7, eye_y - self.eye_size*0.7,
                left_eye_x + self.eye_size*0.7, eye_y + self.eye_size*0.7,
                fill=eye_col, outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size*0.7, eye_y - self.eye_size*0.7,
                right_eye_x + self.eye_size*0.7, eye_y + self.eye_size*0.7,
                fill=eye_col, outline='', width=1
            )
            
            # Draw pupils
            self.canvas.create_oval(
                left_eye_x - 4, eye_y - 3,
                left_eye_x + 2, eye_y + 2,
                fill='#333333', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 4, eye_y - 3,
                right_eye_x + 2, eye_y + 2,
                fill='#333333', outline='', width=1
            )
            
            # Draw soft eye highlights
            self.canvas.create_oval(
                left_eye_x - 2, eye_y - 2,
                left_eye_x, eye_y,
                fill='#FFFFFF', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 2, eye_y - 2,
                right_eye_x, eye_y,
                fill='#FFFFFF', outline='', width=1
            )
        else:
            # Draw closed eyes (sleepy, gentle)
            self.canvas.create_arc(
                left_eye_x - self.eye_size, eye_y - 3,
                left_eye_x + self.eye_size, eye_y + 3,
                start=0, extent=-180, style=tk.ARC, 
                outline='#333333', width=2
            )
            self.canvas.create_arc(
                right_eye_x - self.eye_size, eye_y - 3,
                right_eye_x + self.eye_size, eye_y + 3,
                start=0, extent=-180, style=tk.ARC, 
                outline='#333333', width=2
            )
        
        # Draw mouth with animation state
        mouth_y = 95 + self.bounce_height
        if self.interaction_state == "happy" or self.interaction_state == "excited":
            # Happier, more curved smile
            self.canvas.create_arc(
                100 + body_x_offset - self.mouth_width//2, 
                mouth_y - self.mouth_height//4,
                100 + body_x_offset + self.mouth_width//2, 
                mouth_y + self.mouth_height//4,
                start=10, extent=-160, style=tk.ARC, 
                fill='', outline=self.mouth_color, width=2
            )
        elif self.interaction_state == "thinking":
            # Straight line for thinking
            self.canvas.create_line(
                100 + body_x_offset - self.mouth_width//2, 
                mouth_y,
                100 + body_x_offset + self.mouth_width//2, 
                mouth_y,
                fill='#8B4513', width=2
            )
        elif self.interaction_state == "sleeping":
            # Sleepy zzz line
            self.canvas.create_arc(
                100 + body_x_offset - self.mouth_width//2, 
                mouth_y - self.mouth_height//4,
                100 + body_x_offset + self.mouth_width//2, 
                mouth_y + self.mouth_height//4,
                start=10, extent=-180, style=tk.ARC, 
                fill='', outline='#A9A9A9', width=1
            )
        else:
            # Default gentle smile
            self.canvas.create_arc(
                100 + body_x_offset - self.mouth_width//2, 
                mouth_y - self.mouth_height//4,
                100 + body_x_offset + self.mouth_width//2, 
                mouth_y + self.mouth_height//4,
                start=10, extent=-160, style=tk.ARC, 
                fill='', outline=self.mouth_color, width=2
            )
        
        # Draw blush (adjust based on state)
        if self.interaction_state in ["happy", "excited", "responding"]:
            self.canvas.create_oval(
                80 + body_x_offset, 85 + self.bounce_height, 
                90 + body_x_offset, 95 + self.bounce_height,
                fill='#FFD1DC', outline='', stipple='gray25'
            )
            self.canvas.create_oval(
                110 + body_x_offset, 85 + self.bounce_height, 
                120 + body_x_offset, 95 + self.bounce_height,
                fill='#FFD1DC', outline='', stipple='gray25'
            )
    
    def animate_idle(self):
        """Idle animation - gentle floating"""
        self.float_offset += self.animation_speed
        self.wing_flap += 0.1 * self.wing_flap_direction
        if abs(self.wing_flap) > 1:
            self.wing_flap_direction *= -1
    
    def animate_listening(self):
        """Listening animation - slight alert movements"""
        self.float_offset += self.animation_speed * 1.2  # Slightly faster float
        self.wing_flap += 0.15 * self.wing_flap_direction
        if abs(self.wing_flap) > 1.5:
            self.wing_flap_direction *= -1
    
    def animate_responding(self):
        """Responding animation - more active movements"""
        self.float_offset += self.animation_speed * 1.5  # Faster float
        self.bounce_height += 0.2 * self.bounce_direction
        if abs(self.bounce_height) > 5:
            self.bounce_direction *= -1
        self.wing_flap += 0.2 * self.wing_flap_direction
        if abs(self.wing_flap) > 2:
            self.wing_flap_direction *= -1
    
    def animate_happy(self):
        """Happy animation - bouncy and cheerful"""
        self.float_offset += self.animation_speed * 2  # Much faster float
        self.bounce_height += 0.3 * self.bounce_direction
        if abs(self.bounce_height) > 8:
            self.bounce_direction *= -1
        self.wing_flap += 0.25 * self.wing_flap_direction
        if abs(self.wing_flap) > 2.5:
            self.wing_flap_direction *= -1
    
    def animate_excited(self):
        """Excited animation - very active"""
        self.float_offset += self.animation_speed * 3  # Very fast float
        self.bounce_height += 0.4 * self.bounce_direction
        if abs(self.bounce_height) > 10:
            self.bounce_direction *= -1
        self.wing_flap += 0.3 * self.wing_flap_direction
        if abs(self.wing_flap) > 3:
            self.wing_flap_direction *= -1
    
    def animate_thinking(self):
        """Thinking animation - slower, contemplative"""
        self.float_offset += self.animation_speed * 0.5  # Slower float
        self.wing_flap += 0.05 * self.wing_flap_direction
        if abs(self.wing_flap) > 0.5:
            self.wing_flap_direction *= -1
        # Occasional slight tilt
        if int(self.float_offset) % 100 == 0:
            self.bounce_direction *= -1
    
    def animate_sleeping(self):
        """Sleeping animation - very slow, gentle"""
        self.float_offset += self.animation_speed * 0.2  # Very slow float
        self.wing_flap += 0.02 * self.wing_flap_direction
        if abs(self.wing_flap) > 0.2:
            self.wing_flap_direction *= -1
    
    def animate(self):
        """Main animation loop"""
        # Update animation values
        self.animation_frame += 1
        
        # Handle interaction timer
        if self.interaction_timer > 0:
            self.interaction_timer -= 1
            if self.interaction_timer <= 0:
                self.interaction_state = "idle"
        
        # Handle blinking
        self.eye_blink_counter += 1
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            # Random blink chance
            if random.randint(0, 200) == 0:  # Random blink
                self.blink_state = False
                self.blink_timer = 30  # 30 frames blink
        
        # Update position based on animation
        self.bounce_height += 0.05 * self.bounce_direction
        if self.bounce_height > 3:
            self.bounce_direction = -1
        elif self.bounce_height < -3:
            self.bounce_direction = 1
            
        # Update wing flap
        self.wing_flap += 0.1 * self.wing_flap_direction
        if abs(self.wing_flap) > 2:
            self.wing_flap_direction *= -1
        
        # Redraw avatar
        self.draw_avatar()
        
        # Schedule next animation frame
        self.root.after(50, self.animate)  # ~20 FPS
    
    def on_drag_start(self, event):
        """Begin dragging the avatar"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["start_x"] = self.x
        self.drag_data["start_y"] = self.y
    
    def on_drag(self, event):
        """Handle dragging the avatar"""
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
        """Stop dragging the avatar"""
        pass
    
    def cycle_animation(self, event):
        """Cycle through different animations"""
        animation_list = list(self.animations.keys())
        current_index = animation_list.index(self.current_animation)
        next_index = (current_index + 1) % len(animation_list)
        self.current_animation = animation_list[next_index]
        
        # Set interaction state to match animation
        self.set_interaction_state(self.current_animation, 600)
    
    def set_interaction_state(self, state, duration=300):  # Duration in animation frames
        """Set the interaction state of the avatar"""
        self.interaction_state = state
        self.interaction_timer = duration
    
    def appear(self, message=""):
        """Make the avatar appear and optionally speak"""
        self.visible = True
        self.set_interaction_state("responding", 300)
        self.current_animation = "responding"
        self.draw_avatar()
        
        # Excited bounce to indicate appearance
        self.bounce_direction = -2
        
        if message:
            play_girly_response(message)
        else:
            # Play a gentle ping when appearing without message
            play_girly_ping()
    
    def listen_mode(self):
        """Set avatar to listening mode"""
        self.set_interaction_state("listening", 600)
        self.current_animation = "listening"
    
    def happy_mode(self):
        """Set avatar to happy mode"""
        self.set_interaction_state("happy", 200)
        self.current_animation = "happy"
    
    def excited_mode(self):
        """Set avatar to excited mode"""
        self.set_interaction_state("excited", 200)
        self.current_animation = "excited"
    
    def thinking_mode(self):
        """Set avatar to thinking mode"""
        self.set_interaction_state("thinking", 400)
        self.current_animation = "thinking"
    
    def sleeping_mode(self):
        """Set avatar to sleeping mode"""
        self.set_interaction_state("sleeping", 1000)
        self.current_animation = "sleeping"
    
    def disappear(self):
        """Make the avatar gently disappear"""
        self.visible = False
        self.canvas.delete("all")
    
    def run(self):
        """Start the animated avatar system"""
        self.root.mainloop()


def main():
    print("Starting MIST Animated Avatar System...")
    print("Comprehensive animated fairy avatar with multiple animation sets.")
    print("Double-click the avatar to cycle through different animations.")
    
    avatar = MISTAnimatedAvatar()
    
    # Example: Make avatar appear with a message
    def demo_appear():
        avatar.appear("Hello, sister! I'm your animated MIST avatar with multiple animation sets! Double-click me to see different animations!")
    
    # Schedule demo appearance after 2 seconds
    avatar.root.after(2000, demo_appear)
    
    avatar.run()


if __name__ == "__main__":
    main()