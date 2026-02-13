"""
Floating Fairy Avatar for MIST Companion
Animated fairy that appears when MIST responds
Centered version for better visibility
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
                freq, duration = SPEECH_PATTERNS['?']
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


class FloatingFairy:
    def __init__(self):
        # Create transparent window for the fairy
        self.root = tk.Tk()
        self.root.title("MIST Fairy")
        self.root.geometry("200x200")
        self.root.configure(bg='white')
        self.root.attributes('-transparentcolor', 'white')
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Position fairy in center of screen initially
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = (screen_width // 2) - 100  # Center position
        self.y = (screen_height // 2) - 100  # Center position
        self.root.geometry(f"200x200+{self.x}+{self.y}")
        
        # Create canvas for drawing fairy
        self.canvas = tk.Canvas(
            self.root, 
            width=200, 
            height=200, 
            bg='white', 
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Fairy properties (larger for better visibility)
        self.size = 80
        self.eye_size = 12
        self.eye_offset_x = 20
        self.eye_offset_y = 15
        self.mouth_width = 25
        self.mouth_height = 15
        
        # Colors
        self.skin_color = '#F5F5DC'  # Light beige
        self.eye_color = '#6B8E23'   # Olive green
        self.mouth_color = '#FF69B4' # Hot pink
        self.wing_color = '#B0E0E6'  # Light blue
        self.hair_color = '#D8BFD8'  # Thistle
        self.glow_color = '#E6F3FF'  # Soft blue glow
        
        # Animation properties
        self.float_offset = 0
        self.blink_state = True
        self.blink_timer = 0
        self.animation_phase = 0
        self.visible = True
        self.bounce_height = 0
        self.bounce_direction = 1
        
        # Draw initial fairy
        self.draw_fairy()
        
        # Start animation
        self.animate()
        
        # Bind click to move fairy
        self.canvas.bind("<Button-1>", self.move_fairy)
        
        # Bind double-click to make fairy dance
        self.canvas.bind("<Double-Button-1>", self.dance_fairy)
    
    def draw_fairy(self):
        """Draw the fairy avatar"""
        self.canvas.delete("all")
        
        if not self.visible:
            return
            
        # Calculate floating position
        float_y = self.y + math.sin(self.float_offset) * 8
        
        # Draw outer glow
        self.canvas.create_oval(
            self.x + 30, self.y + 20,
            self.x + 50 + self.size, self.y + 40 + self.size,
            fill=self.glow_color, outline='', stipple='gray50'
        )
        
        # Draw wings (more prominent)
        wing_x = self.x + 10
        wing_y = self.y + 30
        self.canvas.create_oval(
            wing_x - 40, wing_y - 30,
            wing_x + 40, wing_y + 30,
            fill=self.wing_color, outline='', stipple='gray25'
        )
        
        wing_x = self.x + 130
        self.canvas.create_oval(
            wing_x - 40, wing_y - 30,
            wing_x + 40, wing_y + 30,
            fill=self.wing_color, outline='', stipple='gray25'
        )
        
        # Draw main body/head
        self.canvas.create_oval(
            self.x + 60, self.y + 40,
            self.x + 60 + self.size, self.y + 40 + self.size,
            fill=self.skin_color, outline='#DDEEFF', width=3
        )
        
        # Draw hair/halo effect
        self.canvas.create_oval(
            self.x + 55, self.y + 35,
            self.x + 65 + self.size, self.y + 45 + self.size,
            outline=self.hair_color, width=3, dash=(6, 6)
        )
        
        # Draw eyes
        left_eye_x = self.x + 75
        right_eye_x = self.x + 115
        eye_y = self.y + 60
        
        if self.blink_state:
            # Draw open eyes (larger for visibility)
            self.canvas.create_oval(
                left_eye_x - self.eye_size, eye_y - self.eye_size,
                left_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#CCCCCC', width=2
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size, eye_y - self.eye_size,
                right_eye_x + self.eye_size, eye_y + self.eye_size,
                fill='white', outline='#CCCCCC', width=2
            )
            
            # Draw irises
            self.canvas.create_oval(
                left_eye_x - self.eye_size*0.6, eye_y - self.eye_size*0.6,
                left_eye_x + self.eye_size*0.6, eye_y + self.eye_size*0.6,
                fill=self.eye_color, outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_size*0.6, eye_y - self.eye_size*0.6,
                right_eye_x + self.eye_size*0.6, eye_y + self.eye_size*0.6,
                fill=self.eye_color, outline='', width=1
            )
            
            # Draw pupils
            self.canvas.create_oval(
                left_eye_x - 4, eye_y - 3,
                left_eye_x + 3, eye_y + 3,
                fill='#000000', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 4, eye_y - 3,
                right_eye_x + 3, eye_y + 3,
                fill='#000000', outline='', width=1
            )
            
            # Draw eye highlights
            self.canvas.create_oval(
                left_eye_x - 2, eye_y - 2,
                left_eye_x - 0.5, eye_y - 0.5,
                fill='#FFFFFF', outline='', width=1
            )
            self.canvas.create_oval(
                right_eye_x - 2, eye_y - 2,
                right_eye_x - 0.5, eye_y - 0.5,
                fill='#FFFFFF', outline='', width=1
            )
        else:
            # Draw closed eyes (horizontal lines)
            self.canvas.create_line(
                left_eye_x - self.eye_size, eye_y,
                left_eye_x + self.eye_size, eye_y,
                fill='#000000', width=3
            )
            self.canvas.create_line(
                right_eye_x - self.eye_size, eye_y,
                right_eye_x + self.eye_size, eye_y,
                fill='#000000', width=3
            )
        
        # Draw mouth
        mouth_y = self.y + 90
        self.canvas.create_arc(
            self.x + 95 - self.mouth_width//2, 
            mouth_y - self.mouth_height//4,
            self.x + 95 + self.mouth_width//2, 
            mouth_y + self.mouth_height//4,
            start=0, extent=-90, style=tk.ARC, 
            fill='', outline=self.mouth_color, width=3
        )
        
        # Draw name tag
        self.canvas.create_rectangle(
            self.x + 75, self.y + 130,
            self.x + 125, self.y + 150,
            fill=self.hair_color, outline=self.eye_color, width=2
        )
        self.canvas.create_text(
            self.x + 100, self.y + 140,
            text="MIST", fill=self.eye_color, font=('Arial', 12, 'bold')
        )
    
    def animate(self):
        """Animate the fairy"""
        # Update animation values
        self.float_offset += 0.1
        self.animation_phase += 0.05
        
        # Handle blinking
        if self.blink_timer > 0:
            self.blink_timer -= 0.05
            if self.blink_timer <= 0:
                self.blink_state = True
        else:
            # Random blink chance
            import random
            if random.random() < 0.005:  # Small chance to blink
                self.blink_state = False
                self.blink_timer = 0.2  # Blink for 0.2 seconds
        
        # Update position based on bounce
        self.bounce_height += 0.1 * self.bounce_direction
        if self.bounce_height > 5:
            self.bounce_direction = -1
        elif self.bounce_height < -5:
            self.bounce_direction = 1
            
        # Redraw fairy
        self.draw_fairy()
        
        # Schedule next animation frame
        self.root.after(50, self.animate)  # ~20 FPS
    
    def move_fairy(self, event):
        """Move fairy to a new position when clicked"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate new random position (keeping within screen bounds)
        new_x = max(0, min(screen_width - 200, event.x_root - 100))
        new_y = max(0, min(screen_height - 200, event.y_root - 100))
        
        self.x = new_x
        self.y = new_y
        self.root.geometry(f"200x200+{self.x}+{self.y}")
    
    def dance_fairy(self, event):
        """Make the fairy do a little dance"""
        # Move to a random position near the click
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        new_x = max(0, min(screen_width - 200, event.x_root - 100))
        new_y = max(0, min(screen_height - 200, event.y_root - 100))
        
        self.x = new_x
        self.y = new_y
        self.root.geometry(f"200x200+{self.x}+{self.y}")
        
        # Bounce animation
        self.bounce_direction = -3  # Strong upward bounce
    
    def appear(self, message=""):
        """Make the fairy appear and optionally speak"""
        self.visible = True
        self.draw_fairy()
        
        # Make fairy bounce to indicate appearance
        self.bounce_direction = -2  # Strong upward bounce
        
        if message:
            speak_text_threaded(message)
    
    def disappear(self):
        """Make the fairy temporarily disappear"""
        self.visible = False
        self.canvas.delete("all")
    
    def run(self):
        """Start the fairy"""
        self.root.mainloop()


def main():
    print("Starting Floating Fairy Avatar for MIST...")
    print("A fairy avatar will appear in the CENTER of your screen.")
    print("It will appear when MIST responds and can be moved by clicking it.")
    
    fairy = FloatingFairy()
    
    # Example: Make fairy appear with a message
    # In a real implementation, this would be called when MIST responds
    def demo_appear():
        fairy.appear("Hello, sister! I'm your floating fairy companion! Click me to move me around!")
    
    # Schedule demo appearance after 2 seconds
    fairy.root.after(2000, demo_appear)
    
    fairy.run()


if __name__ == "__main__":
    main()