"""
Notification Avatar for MIST Companion
More noticeable avatar that appears when MIST responds
"""

import tkinter as tk
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


class NotificationAvatar:
    def __init__(self):
        # Create a more noticeable window
        self.root = tk.Tk()
        self.root.title("MIST Notification")
        self.root.geometry("300x200")
        self.root.configure(bg='#E6F3FF')
        
        # Position in upper right corner for better visibility
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - 320
        self.y = 20
        self.root.geometry(f"300x200+{self.x}+{self.y}")
        
        # Make it stay on top
        self.root.attributes('-topmost', True)
        
        # Create canvas for avatar
        self.canvas = tk.Canvas(
            self.root,
            width=300,
            height=200,
            bg='#E6F3FF',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw avatar
        self.draw_avatar()
        
        # Add a close button
        close_button = tk.Button(
            self.root,
            text="×",
            command=self.hide_notification,
            bg='#FF6B6B',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.FLAT,
            bd=0,
            width=2,
            height=1
        )
        close_button.place(x=275, y=5)
        
        # Auto-hide after 10 seconds
        self.root.after(10000, self.hide_notification)
        
        # Bind click to move to different positions
        self.canvas.bind("<Button-1>", self.cycle_position)
        
        # Counter for cycling positions
        self.position_cycle = 0
        self.positions = [
            (screen_width - 320, 20),      # Top right
            (20, 20),                      # Top left
            (20, screen_height - 220),     # Bottom left
            (screen_width - 320, screen_height - 220)  # Bottom right
        ]
    
    def draw_avatar(self):
        """Draw the avatar with clear, recognizable features"""
        self.canvas.delete("all")
        
        # Draw soft background
        self.canvas.create_rectangle(0, 0, 300, 200, fill='#E6F3FF', outline='')
        
        # Draw head
        self.canvas.create_oval(100, 40, 200, 140, fill='#F5F5DC', outline='#DDEEFF', width=3)
        
        # Draw large, clear eyes
        # Left eye
        self.canvas.create_oval(120, 70, 140, 90, fill='white', outline='#CCCCCC', width=2)
        self.canvas.create_oval(125, 75, 135, 85, fill='#6B8E23', outline='', width=1)  # Green iris
        self.canvas.create_oval(128, 78, 132, 82, fill='black', outline='', width=1)  # Pupil
        # Eye highlight
        self.canvas.create_oval(129, 79, 131, 81, fill='white', outline='', width=1)
        
        # Right eye
        self.canvas.create_oval(160, 70, 180, 90, fill='white', outline='#CCCCCC', width=2)
        self.canvas.create_oval(165, 75, 175, 85, fill='#6B8E23', outline='', width=1)  # Green iris
        self.canvas.create_oval(168, 78, 172, 82, fill='black', outline='', width=1)  # Pupil
        # Eye highlight
        self.canvas.create_oval(169, 79, 171, 81, fill='white', outline='', width=1)
        
        # Draw clear smile
        self.canvas.create_arc(140, 100, 160, 120, start=0, extent=-180, style=tk.ARC, 
                               outline='#FF69B4', width=3)
        
        # Draw hair/halo effect
        self.canvas.create_oval(95, 35, 205, 145, outline='#D8BFD8', width=3, dash=(6, 6))
        
        # Draw name
        self.canvas.create_text(150, 160, text="MIST", fill='#6B8E23', font=('Arial', 16, 'bold'))
        
        # Draw "New Message" indicator
        self.canvas.create_oval(250, 40, 280, 70, fill='#98FB98', outline='#6B8E23', width=2)
        self.canvas.create_text(265, 55, text="NEW", fill='#6B8E23', font=('Arial', 10, 'bold'))
    
    def cycle_position(self, event=None):
        """Cycle through different positions on screen"""
        self.position_cycle = (self.position_cycle + 1) % len(self.positions)
        x, y = self.positions[self.position_cycle]
        self.root.geometry(f"300x200+{x}+{y}")
    
    def show_notification(self, message=""):
        """Show the notification avatar"""
        self.root.deiconify()  # Make sure it's visible
        self.draw_avatar()
        
        # Bring to front
        self.root.lift()
        self.root.focus_force()
        
        # Reset auto-hide timer
        self.root.after_cancel(self.root.after(10000, self.hide_notification))
        self.root.after(10000, self.hide_notification)
        
        if message:
            speak_text_threaded(message)
    
    def hide_notification(self):
        """Hide the notification"""
        self.root.withdraw()  # Hide the window
    
    def run(self):
        """Start the notification system"""
        self.root.mainloop()


def main():
    print("Starting Notification Avatar for MIST...")
    print("A more noticeable avatar will appear when MIST responds.")
    print("It will show in the corner of your screen with clear features.")
    
    avatar = NotificationAvatar()
    
    # Example: Show notification with a message
    # In a real implementation, this would be called when MIST responds
    def demo_show():
        avatar.show_notification("Hello, sister! I'm your MIST companion. I'm here when you need me!")
    
    # Schedule demo notification after 2 seconds
    avatar.root.after(2000, demo_show)
    
    avatar.run()


if __name__ == "__main__":
    main()