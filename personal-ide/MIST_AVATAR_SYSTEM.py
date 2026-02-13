"""
MIST Avatar System
Official animated fairy avatar for the MIST companion system
"""

import tkinter as tk
import math
import time
import threading
import winsound
from datetime import datetime


# Simple beep patterns to simulate speech
SPEECH_PATTERNS = {
    'a': (523, 100),   # C note
    'e': (587, 100),   # D note
    'i': (659, 100),   # E note
    'o': (698, 100),   # F note
    'u': (784, 100),   # G note
    ' ': (300, 150),   # Rest
    '.': (400, 200),   # Period pause
    ',': (350, 100),   # Comma pause
    '!': (800, 150),   # Exclamation emphasis
    '?': (750, 150),   # Question emphasis
}

def simple_speak_text(text):
    """
    Very simple text-to-speech using beeps
    In a real implementation, this would use actual TTS
    """
    text = text.lower()
    for char in text:
        if char in 'aeiou':
            freq, duration = SPEECH_PATTERNS[char]
            try:
                winsound.Beep(freq, duration)
            except:
                # Beep might not work on all systems, just continue
                pass
            time.sleep(duration/1000.0)
        elif char in ' .,!?':
            # Handle punctuation
            if char == '.':
                freq, duration = SPEECH_PATTERNS['.']
                try:
                    winsound.Beep(freq, duration)
                except:
                    pass
                time.sleep(duration/1000.0)
            elif char == '!':
                freq, duration = SPEECH_PATTERNS['!']
                try:
                    winsound.Beep(freq, duration)
                except:
                    pass
                time.sleep(duration/1000.0)
            elif char == '?':
                freq, duration = SPEARCH_PATTERNS['?']
                try:
                    winsound.Beep(freq, duration)
                except:
                    pass
                time.sleep(duration/1000.0)
            elif char == ' ':
                freq, duration = SPEECH_PATTERNS[' ']
                time.sleep(duration/1000.0)
        else:
            # Use a default note for consonants
            try:
                winsound.Beep(600, 80)
            except:
                pass
            time.sleep(0.08)

def speak_text_threaded(text):
    """Speak text in a separate thread to avoid blocking"""
    thread = threading.Thread(target=simple_speak_text, args=(text,))
    thread.daemon = True
    thread.start()


class MISTAvatar:
    def __init__(self):
        # Create a transparent window for the avatar
        self.root = tk.Tk()
        self.root.title("MIST Avatar")
        
        # Set transparency and attributes
        self.root.configure(bg='white')
        self.root.attributes('-transparentcolor', 'white')  # Make white transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations
        
        # Size the window appropriately for the avatar
        self.root.geometry("150x150")
        
        # Position avatar initially in upper right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - 200
        self.y = 50
        self.root.geometry(f"150x150+{self.x}+{self.y}")
        
        # Create canvas for drawing avatar
        self.canvas = tk.Canvas(
            self.root,
            width=150,
            height=150,
            bg='white',  # This will be transparent
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Avatar properties (our official MIST fairy design)
        self.size = 50
        self.eye_size = 10
        self.eye_offset_x = 12
        self.eye_offset_y = 8
        self.mouth_width = 15
        self.mouth_height = 8
        
        # Official MIST colors
        self.skin_color = '#FFF8DC'  # Cornsilk (lighter, warmer)
        self.eye_color = '#98FB98'   # Pale green (gentle, caring)
        self.mouth_color = '#FFB6C1' # Light pink (soft)
        self.wing_color = '#E6E6FA'  # Lavender (gentle)
        self.hair_color = '#FFE4E1'  # Misty rose (soft)
        self.glow_color = '#F0F8FF'  # Alice blue (soft)
        self.body_outline = '#F5F5DC' # Beige outline
        
        # Animation states
        self.float_offset = 0
        self.blink_state = True
        self.blink_timer = 0
        self.animation_phase = 0
        self.visible = True
        self.bounce_height = 0
        self.bounce_direction = 1
        self.interaction_state = "idle"  # idle, listening, responding, happy, sad
        self.interaction_timer = 0
        
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
        
        # Bind double-click to reset position
        self.canvas.bind("<Double-Button-1>", self.reset_position)
    
    def draw_avatar(self):
        """Draw the official MIST avatar (fairy)"""
        self.canvas.delete("all")
        
        if not self.visible:
            return
            
        # Adjust colors based on interaction state
        if self.interaction_state == "listening":
            # Brighter colors when listening
            skin_col = '#FFFACD'  # Lemon chiffon
            eye_col = '#ADFF2F'   # Green yellow
        elif self.interaction_state == "responding":
            # Warm colors when responding
            skin_col = '#FFF8DC'  # Cornsilk
            eye_col = '#98FB98'   # Pale green
        elif self.interaction_state == "happy":
            # Rosy colors when happy
            skin_col = '#FFF0F5'  # Lavender blush
            eye_col = '#AFEEEE'   # Pale turquoise
        elif self.interaction_state == "sad":
            # Softer colors when sad
            skin_col = '#FDF5E6'  # Old lace
            eye_col = '#BC8F8F'   # Rosy brown
        else:
            # Default colors
            skin_col = self.skin_color
            eye_col = self.eye_color
        
        # Draw outer soft glow (halo effect)
        self.canvas.create_oval(
            35, 25, 115, 105,
            fill=self.glow_color, outline='', stipple='gray50'
        )
        
        # Draw wings (adjust based on interaction state)
        wing_opacity = '' if self.interaction_state != "responding" else 'gray10'
        
        # Left wing
        wing_points = [
            10, 40,  # Wing tip
            40, 30,  # Upper attachment
            40, 60,  # Lower attachment
        ]
        self.canvas.create_polygon(wing_points, fill=self.wing_color, outline='', stipple=wing_opacity)
        
        # Right wing
        wing_points = [
            140, 40,  # Wing tip
            110, 30,  # Upper attachment
            110, 60,  # Lower attachment
        ]
        self.canvas.create_polygon(wing_points, fill=self.wing_color, outline='', stipple=wing_opacity)
        
        # Draw main body/head
        self.canvas.create_oval(
            50, 40, 100, 90,
            fill=skin_col, outline=self.body_outline, width=2
        )
        
        # Draw hair/halo effect
        self.canvas.create_oval(
            45, 35, 105, 95,
            outline=self.hair_color, width=2, dash=(3, 3)
        )
        
        # Draw eyes
        left_eye_x = 62
        right_eye_x = 88
        eye_y = 58
        
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
        
        # Draw mouth (expression varies by state)
        mouth_y = self.y + 72
        if self.interaction_state == "happy":
            # Happier, more curved smile
            self.canvas.create_arc(
                72 - self.mouth_width//2, 
                mouth_y - self.mouth_height//4,
                72 + self.mouth_width//2, 
                mouth_y + self.mouth_height//4,
                start=10, extent=-160, style=tk.ARC, 
                fill='', outline=self.mouth_color, width=2
            )
        elif self.interaction_state == "sad":
            # Sad, downturned mouth
            self.canvas.create_arc(
                72 - self.mouth_width//2, 
                mouth_y + self.mouth_height//4,
                72 + self.mouth_width//2, 
                mouth_y + self.mouth_height + 5,
                start=10, extent=160, style=tk.ARC, 
                fill='', outline='#D8BFD8', width=2
            )
        else:
            # Default gentle smile
            self.canvas.create_arc(
                72 - self.mouth_width//2, 
                mouth_y - self.mouth_height//4,
                72 + self.mouth_width//2, 
                mouth_y + self.mouth_height//4,
                start=10, extent=-160, style=tk.ARC, 
                fill='', outline=self.mouth_color, width=2
            )
        
        # Draw blush (adjust based on state)
        if self.interaction_state in ["happy", "responding"]:
            self.canvas.create_oval(
                55, 70, 65, 80,
                fill='#FFD1DC', outline='', stipple='gray25'
            )
            self.canvas.create_oval(
                85, 70, 95, 80,
                fill='#FFD1DC', outline='', stipple='gray25'
            )
    
    def animate(self):
        """Animate the avatar with various states"""
        # Update animation values
        self.float_offset += 0.05  # Slower float for gentler movement
        self.animation_phase += 0.03
        
        # Handle interaction timer
        if self.interaction_timer > 0:
            self.interaction_timer -= 1
            if self.interaction_timer <= 0:
                self.interaction_state = "idle"
        
        # Handle blinking
        if self.blink_timer > 0:
            self.blink_timer -= 0.05
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            # Higher chance to blink for friendlier look
            import random
            if random.random() < 0.01:  # More frequent blinks
                self.blink_state = False
                self.blink_timer = 0.25
        
        # Update position based on gentle bounce
        self.bounce_height += 0.05 * self.bounce_direction
        if self.bounce_height > 2:
            self.bounce_direction = -1
        elif self.bounce_height < -2:
            self.bounce_direction = 1
            
        # Redraw avatar
        self.draw_avatar()
        
        # Schedule next animation frame
        self.root.after(60, self.animate)
    
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
        self.root.geometry(f"150x150+{self.x}+{self.y}")
    
    def on_drag_stop(self, event):
        """Stop dragging the avatar"""
        pass
    
    def reset_position(self, event):
        """Reset avatar to default position"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - 200
        self.y = 50
        self.root.geometry(f"150x150+{self.x}+{self.y}")
    
    def set_interaction_state(self, state, duration=300):  # Duration in animation frames
        """Set the interaction state of the avatar"""
        self.interaction_state = state
        self.interaction_timer = duration
    
    def appear(self, message=""):
        """Make the avatar appear and optionally speak"""
        self.visible = True
        self.set_interaction_state("responding", 300)  # Responding for 300 frames
        self.draw_avatar()
        
        # Gentle bounce to indicate appearance
        self.bounce_direction = -1.5
        
        if message:
            speak_text_threaded(message)
    
    def listen_mode(self):
        """Set avatar to listening mode"""
        self.set_interaction_state("listening", 600)  # Listening for 600 frames
    
    def happy_mode(self):
        """Set avatar to happy mode"""
        self.set_interaction_state("happy", 200)  # Happy for 200 frames
    
    def sad_mode(self):
        """Set avatar to sad mode"""
        self.set_interaction_state("sad", 200)  # Sad for 200 frames
    
    def disappear(self):
        """Make the avatar gently disappear"""
        self.visible = False
        self.canvas.delete("all")
    
    def run(self):
        """Start the avatar system"""
        self.root.mainloop()


def main():
    print("Starting MIST Avatar System...")
    print("Official animated fairy avatar for the MIST companion system.")
    print("This is our dedicated avatar with various interaction states.")
    
    avatar = MISTAvatar()
    
    # Example: Make avatar appear with a message
    def demo_appear():
        avatar.appear("Hello, sister! This is our official MIST avatar - your gentle fairy companion!")
    
    # Schedule demo appearance after 2 seconds
    avatar.root.after(2000, demo_appear)
    
    avatar.run()


if __name__ == "__main__":
    main()