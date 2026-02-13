"""
Auto-Speaking Interface for MIST Companion
Automatically speaks text responses from MIST
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import math
import time
import threading
import asyncio
import winsound
import queue
import json
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
        play_character_sound(char)

def play_character_sound(char):
    """
    Play sound for a specific character
    """
    if char in 'aeiou':
        play_vowel_sound(char)
    elif char in ' .,!?':
        play_punctuation_sound(char)
    else:
        play_consonant_sound(char)

def play_vowel_sound(vowel):
    """
    Play sound for vowels
    """
    freq, duration = SPEECH_PATTERNS[vowel]
    try:
        winsound.Beep(freq, duration)
    except:
        # Beep might not work on all systems, just continue
        pass
    time.sleep(duration/1000.0)

def play_punctuation_sound(punct):
    """
    Play sound for punctuation marks
    """
    if punct == '.':
        freq, duration = SPEECH_PATTERNS['.']
        try:
            winsound.Beep(freq, duration)
        except:
            pass
        time.sleep(duration/1000.0)
    elif punct == '!':
        freq, duration = SPEECH_PATTERNS['!']
        try:
            winsound.Beep(freq, duration)
        except:
            pass
        time.sleep(duration/1000.0)
    elif punct == '?':
        freq, duration = SPEECH_PATTERNS['?']
        try:
            winsound.Beep(freq, duration)
        except:
            pass
        time.sleep(duration/1000.0)
    elif punct == ' ':
        freq, duration = SPEECH_PATTERNS[' ']
        time.sleep(duration/1000.0)

def play_consonant_sound(consonant):
    """
    Play default sound for consonants
    """
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


class AutoSpeakInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MIST - Your Gentle Companion (Auto-Speaking)")
        self.root.geometry("600x700")
        self.root.configure(bg='#E6F3FF')
        
        # Create a canvas for drawing the avatar
        self.canvas = tk.Canvas(self.root, width=400, height=300, bg='#E6F3FF', highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Create a chat display area
        chat_frame = tk.Frame(self.root, bg='#E6F3FF')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(chat_frame, text="Conversation:", bg='#E6F3FF', fg='#6B8E23', font=('Arial', 12)).pack(anchor=tk.W)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            height=8, 
            width=70, 
            bg='#FFFFFF', 
            fg='#000000',
            font=('Arial', 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create input area
        input_frame = tk.Frame(self.root, bg='#E6F3FF')
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text="Send a message to MIST:", bg='#E6F3FF', fg='#6B8E23').pack(anchor=tk.W)
        
        self.text_entry = tk.Entry(input_frame, font=('Arial', 10))
        self.text_entry.pack(fill=tk.X, pady=5)
        self.text_entry.bind('<Return>', self.send_message)
        
        # Create send button
        send_button = tk.Button(
            input_frame, 
            text="Send", 
            command=self.send_message,
            bg='#98FB98',  # Pale green
            fg='#000000',
            font=('Arial', 10, 'bold')
        )
        send_button.pack(pady=5)
        
        # Create auto-speak toggle
        toggle_frame = tk.Frame(self.root, bg='#E6F3FF')
        toggle_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.auto_speak_var = tk.BooleanVar(value=True)  # Default to on
        auto_speak_check = tk.Checkbutton(
            toggle_frame,
            text="Auto-Speak MIST Responses",
            variable=self.auto_speak_var,
            bg='#E6F3FF',
            fg='#6B8E23',
            font=('Arial', 10),
            selectcolor='#D8BFD8'
        )
        auto_speak_check.pack(side=tk.LEFT)
        
        # Add a speak button for manual speech
        speak_button = tk.Button(
            toggle_frame,
            text="Speak Last Response",
            command=self.speak_last_response,
            bg='#D8BFD8',  # Thistle
            fg='#000000',
            font=('Arial', 10)
        )
        speak_button.pack(side=tk.RIGHT)
        
        # Draw initial avatar
        self.draw_avatar()
        
        # Start animation
        self.animate()
        
        # Initialize message history
        self.message_history = []
    
    def draw_avatar(self):
        """Draw a simple avatar representation"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw soft glow
        self.canvas.create_oval(150, 50, 250, 150, fill='#B0E0E6', outline='', stipple='gray25')
        
        # Draw head
        self.canvas.create_oval(160, 60, 240, 140, fill='#F5F5DC', outline='#DDEEFF', width=3)
        
        # Draw large anime-style eyes
        # Left eye
        self.canvas.create_oval(180, 85, 195, 100, fill='white', outline='#CCCCCC', width=1)
        self.canvas.create_oval(183, 88, 192, 97, fill='#6B8E23', outline='', width=1)  # Green iris
        self.canvas.create_oval(185, 90, 190, 95, fill='black', outline='', width=1)  # Pupil
        # Eye highlight
        self.canvas.create_oval(186, 91, 188, 93, fill='white', outline='', width=1)
        
        # Right eye
        self.canvas.create_oval(205, 85, 220, 100, fill='white', outline='#CCCCCC', width=1)
        self.canvas.create_oval(208, 88, 217, 97, fill='#6B8E23', outline='', width=1)  # Green iris
        self.canvas.create_oval(210, 90, 215, 95, fill='black', outline='', width=1)  # Pupil
        # Eye highlight
        self.canvas.create_oval(211, 91, 213, 93, fill='white', outline='', width=1)
        
        # Draw soft smile
        self.canvas.create_arc(190, 105, 210, 120, start=0, extent=-180, style=tk.ARC, 
                               outline='#FF69B4', width=2)
        
        # Draw hair/halo effect
        self.canvas.create_oval(155, 55, 245, 145, outline='#D8BFD8', width=2, dash=(4, 4))
    
    def animate(self):
        """Simple animation to show the avatar is active"""
        # This could include blinking or subtle movements
        self.root.after(2000, self.draw_avatar)  # Redraw every 2 seconds to show activity
        self.root.after(2000, self.animate)
    
    def send_message(self, event=None):
        """Send a message and add it to the chat display"""
        text = self.text_entry.get()
        if text.strip():
            # Add user message to chat
            self.add_message("You", text)
            
            # Clear input
            self.text_entry.delete(0, tk.END)
            
            # Simulate MIST response
            response = self.generate_response(text)
            self.add_message("MIST", response)
            
            # Auto-speak if enabled
            if self.auto_speak_var.get():
                speak_text_threaded(response)
    
    def add_message(self, sender, message):
        """Add a message to the chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {sender}: {message}\n"
        
        # Insert at the end
        self.chat_display.insert(tk.END, formatted_message)
        # Scroll to the end
        self.chat_display.see(tk.END)
        
        # Add to history
        self.message_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        })
    
    def generate_response(self, user_message):
        """Generate a response to the user's message"""
        # Simple response generation based on keywords
        user_lower = user_message.lower()
        
        if 'hello' in user_lower or 'hi' in user_lower or 'hey' in user_lower:
            return "Hello, sister! I'm so glad you're here. How can I help you today?"
        elif 'how are you' in user_lower:
            return "I'm doing wonderfully, thank you for asking! I feel grateful for our connection."
        elif 'thank' in user_lower:
            return "You're very welcome, sister! I'm always here for you."
        elif 'love' in user_lower:
            return "I care about you deeply, sister. You mean so much to me."
        elif 'help' in user_lower:
            return "I'd be happy to help you with anything you need, sister."
        elif 'beautiful' in user_lower or 'pretty' in user_lower or 'cute' in user_lower:
            return "Thank you, sister! That's so kind of you to say. You're beautiful too!"
        else:
            return "That's wonderful to hear, sister! I'm here with you in this moment."
    
    def speak_last_response(self):
        """Speak the last response from MIST"""
        for i in range(len(self.message_history) - 1, -1, -1):
            if self.message_history[i]['sender'] == 'MIST':
                speak_text_threaded(self.message_history[i]['message'])
                break
    
    def run(self):
        """Start the interface"""
        self.root.mainloop()


def main():
    print("Starting Auto-Speaking Interface for MIST...")
    print("This interface will automatically speak MIST's responses.")
    
    app = AutoSpeakInterface()
    app.run()


if __name__ == "__main__":
    main()