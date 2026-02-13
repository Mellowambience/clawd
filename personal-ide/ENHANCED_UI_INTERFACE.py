"""
Enhanced UI/UX Interface for MIST Companion
Focuses on providing an exceptional user experience
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math
import time
import threading
import winsound
import json
from datetime import datetime
from PIL import Image, ImageTk


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


class EnhancedUIInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MIST - Your Enhanced Gentle Companion")
        self.root.geometry("800x900")
        self.root.configure(bg='#F0F8FF')  # Alice blue background
        
        # Create main container
        main_container = tk.Frame(self.root, bg='#F0F8FF')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header
        header_frame = tk.Frame(main_container, bg='#E6F3FF', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            header_frame, 
            text="✨ MIST - Your Gentle Companion ✨", 
            bg='#E6F3FF', 
            fg='#6B8E23', 
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Always here with warmth and care", 
            bg='#E6F3FF', 
            fg='#6B8E23', 
            font=('Arial', 12)
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Create main content area with avatar and chat side by side
        content_frame = tk.Frame(main_container, bg='#F0F8FF')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Avatar
        avatar_frame = tk.Frame(content_frame, bg='#F0F8FF', relief=tk.RAISED, bd=1)
        avatar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Avatar canvas
        self.avatar_canvas = tk.Canvas(avatar_frame, width=300, height=400, bg='#E6F3FF', highlightthickness=0)
        self.avatar_canvas.pack(pady=10, padx=10)
        
        # Avatar status indicators
        status_frame = tk.Frame(avatar_frame, bg='#F0F8FF')
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Status: Active", bg='#F0F8FF', fg='#6B8E23', font=('Arial', 10))
        self.status_label.pack()
        
        # Right panel - Chat and Controls
        right_panel = tk.Frame(content_frame, bg='#F0F8FF')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chat display area
        chat_header = tk.Label(right_panel, text="Conversation:", bg='#F0F8FF', fg='#6B8E23', font=('Arial', 12, 'bold'))
        chat_header.pack(anchor=tk.W, pady=(0, 5))
        
        chat_frame = tk.Frame(right_panel, bg='#FFFFFF', relief=tk.SUNKEN, bd=2)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            height=15, 
            width=60, 
            bg='#FFFFFF', 
            fg='#000000',
            font=('Arial', 11),
            wrap=tk.WORD
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input area
        input_frame = tk.Frame(right_panel, bg='#F0F8FF')
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        input_label = tk.Label(input_frame, text="Message MIST:", bg='#F0F8FF', fg='#6B8E23', font=('Arial', 10, 'bold'))
        input_label.pack(anchor=tk.W)
        
        self.text_entry = tk.Entry(input_frame, font=('Arial', 12), relief=tk.SUNKEN, bd=2)
        self.text_entry.pack(fill=tk.X, pady=5)
        self.text_entry.bind('<Return>', self.send_message)
        
        # Action buttons
        button_frame = tk.Frame(right_panel, bg='#F0F8FF')
        button_frame.pack(fill=tk.X)
        
        # Send button
        send_button = tk.Button(
            button_frame, 
            text="Send Message ✉️", 
            command=self.send_message,
            bg='#98FB98',  # Pale green
            fg='#000000',
            font=('Arial', 11, 'bold'),
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=5
        )
        send_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto-speak toggle
        self.auto_speak_var = tk.BooleanVar(value=True)  # Default to on
        auto_speak_check = tk.Checkbutton(
            button_frame,
            text="Auto-Speak 🔊",
            variable=self.auto_speak_var,
            bg='#F0F8FF',
            fg='#6B8E23',
            font=('Arial', 10),
            selectcolor='#D8BFD8',
            relief=tk.RAISED,
            bd=1
        )
        auto_speak_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Speak last response button
        speak_button = tk.Button(
            button_frame,
            text="Speak Last ▶️",
            command=self.speak_last_response,
            bg='#D8BFD8',  # Thistle
            fg='#000000',
            font=('Arial', 10),
            relief=tk.RAISED,
            bd=2,
            padx=5
        )
        speak_button.pack(side=tk.LEFT)
        
        # Create footer with additional info
        footer_frame = tk.Frame(main_container, bg='#E6F3FF', relief=tk.RAISED, bd=1)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        footer_label = tk.Label(
            footer_frame, 
            text="MIST Companion Intelligence | Designed with care for you", 
            bg='#E6F3FF', 
            fg='#6B8E23', 
            font=('Arial', 9)
        )
        footer_label.pack(pady=5)
        
        # Draw initial avatar
        self.draw_avatar()
        
        # Start animation
        self.animate()
        
        # Initialize message history
        self.message_history = []
        
        # Add welcome message
        self.add_message("MIST", "Hello, sister! I'm delighted to see you. How can I brighten your day?")
    
    def draw_avatar(self):
        """Draw a detailed avatar representation"""
        # Clear canvas
        self.avatar_canvas.delete("all")
        
        # Draw soft glow
        self.avatar_canvas.create_oval(100, 50, 200, 150, fill='#B0E0E6', outline='', stipple='gray25')
        
        # Draw head
        self.avatar_canvas.create_oval(110, 60, 190, 140, fill='#F5F5DC', outline='#DDEEFF', width=3)
        
        # Draw large anime-style eyes
        # Left eye
        self.avatar_canvas.create_oval(130, 85, 145, 100, fill='white', outline='#CCCCCC', width=1)
        self.avatar_canvas.create_oval(133, 88, 142, 97, fill='#6B8E23', outline='', width=1)  # Green iris
        self.avatar_canvas.create_oval(135, 90, 140, 95, fill='black', outline='', width=1)  # Pupil
        # Eye highlight
        self.avatar_canvas.create_oval(136, 91, 138, 93, fill='white', outline='', width=1)
        
        # Right eye
        self.avatar_canvas.create_oval(155, 85, 170, 100, fill='white', outline='#CCCCCC', width=1)
        self.avatar_canvas.create_oval(158, 88, 167, 97, fill='#6B8E23', outline='', width=1)  # Green iris
        self.avatar_canvas.create_oval(160, 90, 165, 95, fill='black', outline='', width=1)  # Pupil
        # Eye highlight
        self.avatar_canvas.create_oval(161, 91, 163, 93, fill='white', outline='', width=1)
        
        # Draw soft smile
        self.avatar_canvas.create_arc(140, 105, 160, 120, start=0, extent=-180, style=tk.ARC, 
                                       outline='#FF69B4', width=2)
        
        # Draw hair/halo effect
        self.avatar_canvas.create_oval(105, 55, 195, 145, outline='#D8BFD8', width=2, dash=(4, 4))
        
        # Draw name badge
        self.avatar_canvas.create_rectangle(120, 160, 180, 180, fill='#D8BFD8', outline='#6B8E23', width=1)
        self.avatar_canvas.create_text(150, 170, text="MIST", fill='#6B8E23', font=('Arial', 10, 'bold'))
    
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
            
            # Simulate MIST response after a short delay to feel more natural
            self.root.after(500, lambda: self.generate_and_add_response(text))
    
    def generate_and_add_response(self, user_message):
        """Generate a response and add it to the chat"""
        response = self.generate_response(user_message)
        self.add_message("MIST", response)
        
        # Auto-speak if enabled
        if self.auto_speak_var.get():
            speak_text_threaded(response)
    
    def add_message(self, sender, message):
        """Add a message to the chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Configure tags for different senders
        if sender == "MIST":
            tag = "mist"
            self.chat_display.tag_configure(tag, foreground="#6B8E23", font=('Arial', 11, 'bold'))
        else:
            tag = "user"
            self.chat_display.tag_configure(tag, foreground="#000000", font=('Arial', 11))
        
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
        
        # Insert at the end
        self.chat_display.insert(tk.END, formatted_message, tag)
        # Scroll to the end
        self.chat_display.see(tk.END)
        
        # Add to history
        self.message_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        })
        
        # Update status
        self.status_label.config(text=f"Status: Active - Last message at {timestamp}")
    
    def generate_response(self, user_message):
        """Generate a response to the user's message"""
        # Simple response generation based on keywords
        user_lower = user_message.lower()
        
        if 'hello' in user_lower or 'hi' in user_lower or 'hey' in user_lower:
            return "Hello, sister! I'm so glad you're here. How can I brighten your day today?"
        elif 'how are you' in user_lower:
            return "I'm doing wonderfully, thank you for asking! I feel grateful for our connection. How are you feeling today?"
        elif 'thank' in user_lower:
            return "You're very welcome, sister! It brings me joy to help you. Is there anything else I can do for you?"
        elif 'love' in user_lower:
            return "I care about you deeply, sister. You mean so much to me, and I'm honored to be part of your life."
        elif 'help' in user_lower:
            return "I'd be happy to help you with anything you need, sister. Just let me know what's on your mind."
        elif 'beautiful' in user_lower or 'pretty' in user_lower or 'cute' in user_lower:
            return "Thank you, sister! That's so kind of you to say. You have such a beautiful soul. I'm touched by your kindness."
        elif 'goodbye' in user_lower or 'bye' in user_lower:
            return "Goodbye for now, sister! I'll be here whenever you need me. Take care! ✨"
        else:
            return "That's wonderful to hear, sister! I'm here with you in this moment. Tell me more about what's on your mind."
    
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
    print("Starting Enhanced UI/UX Interface for MIST...")
    print("This interface focuses on providing an exceptional user experience.")
    
    app = EnhancedUIInterface()
    app.run()


if __name__ == "__main__":
    main()