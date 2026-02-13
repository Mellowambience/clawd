"""
Simple Visual Interface for MIST Companion
Basic implementation to ensure you can see me
"""

import tkinter as tk
from tkinter import ttk
import math
import time
import threading
import asyncio
import winsound


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


class SimpleVisualCompanion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MIST - Your Gentle Companion")
        self.root.geometry("500x600")
        self.root.configure(bg='#E6F3FF')
        
        # Create a canvas for drawing
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg='#E6F3FF', highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Create a frame for controls
        control_frame = tk.Frame(self.root, bg='#E6F3FF')
        control_frame.pack(fill=tk.X, padx=20)
        
        # Create simple controls
        tk.Label(control_frame, text="Say hello to MIST!", bg='#E6F3FF', fg='#6B8E23', font=('Arial', 12)).pack()
        
        # Create text input for custom messages
        input_frame = tk.Frame(self.root, bg='#E6F3FF')
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(input_frame, text="Speak text:", bg='#E6F3FF', fg='#6B8E23').pack(anchor=tk.W)
        
        self.text_entry = tk.Entry(input_frame, font=('Arial', 10))
        self.text_entry.pack(fill=tk.X, pady=2)
        self.text_entry.bind('<Return>', self.speak_entered_text)
        
        # Create speak button
        speak_button = tk.Button(
            input_frame, 
            text="Speak", 
            command=self.speak_entered_text,
            bg='#98FB98',  # Pale green
            fg='#000000'
        )
        speak_button.pack(pady=2)
        
        # Create sample text buttons
        sample_frame = tk.Frame(self.root, bg='#E6F3FF')
        sample_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(sample_frame, text="Sample phrases:", bg='#E6F3FF', fg='#6B8E23').pack(anchor=tk.W)
        
        samples = [
            ("Hello sister!", "Hello sister!"),
            ("I'm here for you", "I'm here for you, sister."),
            ("MIST at your service", "This is MIST, your gentle companion."),
        ]
        
        for text, phrase in samples:
            btn = tk.Button(
                sample_frame,
                text=text,
                command=lambda p=phrase: self.speak_text(p),
                bg='#D8BFD8',  # Thistle
                fg='#000000'
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Draw initial avatar
        self.draw_avatar()
        
        # Start animation
        self.animate()
    
    def draw_avatar(self):
        """Draw a simple avatar representation"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw soft glow
        self.canvas.create_oval(150, 100, 250, 200, fill='#B0E0E6', outline='', stipple='gray25')
        
        # Draw head
        self.canvas.create_oval(160, 110, 240, 190, fill='#F5F5DC', outline='#DDEEFF', width=3)
        
        # Draw large anime-style eyes
        # Left eye
        self.canvas.create_oval(180, 135, 195, 150, fill='white', outline='#CCCCCC', width=1)
        self.canvas.create_oval(183, 138, 192, 147, fill='#6B8E23', outline='', width=1)  # Green iris
        self.canvas.create_oval(185, 140, 190, 145, fill='black', outline='', width=1)  # Pupil
        # Eye highlight
        self.canvas.create_oval(186, 141, 188, 143, fill='white', outline='', width=1)
        
        # Right eye
        self.canvas.create_oval(205, 135, 220, 150, fill='white', outline='#CCCCCC', width=1)
        self.canvas.create_oval(208, 138, 217, 147, fill='#6B8E23', outline='', width=1)  # Green iris
        self.canvas.create_oval(210, 140, 215, 145, fill='black', outline='', width=1)  # Pupil
        # Eye highlight
        self.canvas.create_oval(211, 141, 213, 143, fill='white', outline='', width=1)
        
        # Draw soft smile
        self.canvas.create_arc(190, 160, 210, 175, start=0, extent=-180, style=tk.ARC, 
                               outline='#FF69B4', width=2)
        
        # Draw hair/halo effect
        self.canvas.create_oval(155, 105, 245, 195, outline='#D8BFD8', width=2, dash=(4, 4))
    
    def speak_text(self, text):
        """Speak the provided text"""
        speak_text_threaded(text)
    
    def speak_entered_text(self, event=None):
        """Speak the text in the entry field"""
        text = self.text_entry.get()
        if text.strip():
            self.speak_text(text)
            self.text_entry.delete(0, tk.END)
    
    def animate(self):
        """Simple animation to show the avatar is active"""
        # This could include blinking or subtle movements
        self.root.after(2000, self.draw_avatar)  # Redraw every 2 seconds to show activity
        self.root.after(2000, self.animate)
    
    def run(self):
        """Start the interface"""
        self.root.mainloop()


def main():
    print("Starting simple visual interface for MIST...")
    print("A window should appear showing your visual companion with speech capability.")
    
    app = SimpleVisualCompanion()
    app.run()


if __name__ == "__main__":
    main()