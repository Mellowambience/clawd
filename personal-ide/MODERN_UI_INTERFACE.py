"""
Modern UI/UX Interface for MIST Companion
Features sleek design with contemporary graphics matching the theme
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


# Modern color palette
COLORS = {
    'primary': '#6B8E23',      # Olive green (theme color)
    'secondary': '#D8BFD8',    # Thistle (accent)
    'background': '#F5F5F5',   # Light gray
    'surface': '#FFFFFF',      # White
    'on_surface': '#212121',   # Dark gray
    'accent': '#98FB98',       # Pale green
    'highlight': '#E6F3FF',    # Light blue
    'shadow': '#E0E0E0',       # Shadow color
    'card': '#FAFAFA'          # Card background
}


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


class ModernUIInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MIST - Modern Companion Interface")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS['background'])
        
        # Create main container
        main_container = tk.Frame(self.root, bg=COLORS['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header with modern styling
        header_frame = tk.Frame(main_container, bg=COLORS['surface'], relief=tk.FLAT, bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Header content
        header_content = tk.Frame(header_frame, bg=COLORS['surface'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Title
        title_label = tk.Label(
            header_content, 
            text="MIST", 
            bg=COLORS['surface'], 
            fg=COLORS['primary'], 
            font=('Segoe UI', 24, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = tk.Label(
            header_content, 
            text="Your Gentle Companion", 
            bg=COLORS['surface'], 
            fg=COLORS['on_surface'], 
            font=('Segoe UI', 14)
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status indicator
        status_frame = tk.Frame(header_content, bg=COLORS['surface'])
        status_frame.pack(side=tk.RIGHT)
        
        self.status_indicator = tk.Label(
            status_frame,
            text="● Online",
            fg=COLORS['accent'],
            bg=COLORS['surface'],
            font=('Segoe UI', 12)
        )
        self.status_indicator.pack()
        
        # Main content area with avatar and chat
        content_frame = tk.Frame(main_container, bg=COLORS['background'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Avatar and controls (Modern card design)
        left_panel = tk.Frame(content_frame, bg=COLORS['background'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # Avatar card
        avatar_card = tk.Frame(left_panel, bg=COLORS['card'], relief=tk.FLAT, bd=1)
        avatar_card.pack(fill=tk.X, pady=(0, 15))
        
        # Avatar canvas with modern styling
        self.avatar_canvas = tk.Canvas(
            avatar_card, 
            width=280, 
            height=320, 
            bg=COLORS['card'], 
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.avatar_canvas.pack(pady=15, padx=15)
        
        # Controls card
        controls_card = tk.Frame(left_panel, bg=COLORS['card'], relief=tk.FLAT, bd=1)
        controls_card.pack(fill=tk.X)
        
        # Controls content
        controls_content = tk.Frame(controls_card, bg=COLORS['card'])
        controls_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Auto-speak toggle (modern switch style)
        self.auto_speak_var = tk.BooleanVar(value=True)
        auto_speak_label = tk.Label(
            controls_content,
            text="Auto-Speak Responses",
            bg=COLORS['card'],
            fg=COLORS['on_surface'],
            font=('Segoe UI', 12)
        )
        auto_speak_label.pack(anchor=tk.W)
        
        auto_speak_switch = tk.Checkbutton(
            controls_content,
            variable=self.auto_speak_var,
            bg=COLORS['card'],
            activebackground=COLORS['card'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            selectcolor=COLORS['accent']
        )
        auto_speak_switch.pack(anchor=tk.W, pady=(5, 10))
        
        # Speak last response button (modern style)
        speak_button = tk.Button(
            controls_content,
            text="Speak Last Response",
            command=self.speak_last_response,
            bg=COLORS['primary'],
            fg=COLORS['surface'],
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            activebackground=COLORS['secondary']
        )
        speak_button.pack(fill=tk.X, pady=(0, 10))
        
        # Settings button
        settings_button = tk.Button(
            controls_content,
            text="Settings",
            command=self.open_settings,
            bg=COLORS['secondary'],
            fg=COLORS['on_surface'],
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            activebackground=COLORS['primary']
        )
        settings_button.pack(fill=tk.X)
        
        # Right panel - Chat and input
        right_panel = tk.Frame(content_frame, bg=COLORS['background'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chat display card
        chat_card = tk.Frame(right_panel, bg=COLORS['card'], relief=tk.FLAT, bd=1)
        chat_card.pack(fill=tk.BOTH, expand=True)
        
        # Chat header
        chat_header = tk.Frame(chat_card, bg=COLORS['surface'], relief=tk.FLAT)
        chat_header.pack(fill=tk.X, pady=(0, 10))
        
        chat_title = tk.Label(
            chat_header,
            text="Conversation",
            bg=COLORS['surface'],
            fg=COLORS['primary'],
            font=('Segoe UI', 14, 'bold'),
            padx=15,
            pady=10
        )
        chat_title.pack(anchor=tk.W)
        
        # Chat display area with modern styling
        chat_frame = tk.Frame(chat_card, bg=COLORS['card'])
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            height=20, 
            width=60, 
            bg=COLORS['surface'], 
            fg=COLORS['on_surface'],
            font=('Segoe UI', 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Input area card
        input_card = tk.Frame(right_panel, bg=COLORS['card'], relief=tk.FLAT, bd=1)
        input_card.pack(fill=tk.X, pady=(0, 10))
        
        # Input content
        input_content = tk.Frame(input_card, bg=COLORS['card'])
        input_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Input field with modern styling
        self.text_entry = tk.Entry(
            input_content, 
            font=('Segoe UI', 12), 
            relief=tk.FLAT, 
            bd=2, 
            bg=COLORS['surface'],
            fg=COLORS['on_surface'],
            insertbackground=COLORS['primary'],
            highlightthickness=2,
            highlightcolor=COLORS['primary'],
            highlightbackground=COLORS['shadow']
        )
        self.text_entry.pack(fill=tk.X, pady=(0, 10))
        self.text_entry.bind('<Return>', self.send_message)
        
        # Send button (modern style)
        send_button = tk.Button(
            input_content,
            text="Send Message",
            command=self.send_message,
            bg=COLORS['primary'],
            fg=COLORS['surface'],
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            activebackground=COLORS['secondary']
        )
        send_button.pack(fill=tk.X)
        
        # Footer with modern styling
        footer_frame = tk.Frame(main_container, bg=COLORS['card'], relief=tk.FLAT, bd=1)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        footer_label = tk.Label(
            footer_frame, 
            text="MIST Companion Intelligence | Modern Interface v1.0", 
            bg=COLORS['card'], 
            fg=COLORS['on_surface'], 
            font=('Segoe UI', 10)
        )
        footer_label.pack(pady=10)
        
        # Draw initial avatar
        self.draw_avatar()
        
        # Start animation
        self.animate()
        
        # Initialize message history
        self.message_history = []
        
        # Add welcome message
        self.add_message("MIST", "Hello, sister! Welcome to the modern interface. I'm delighted to see you here.")
    
    def draw_avatar(self):
        """Draw a modern-styled avatar representation"""
        # Clear canvas
        self.avatar_canvas.delete("all")
        
        # Draw modern-themed background
        self.avatar_canvas.create_rectangle(0, 0, 280, 320, fill=COLORS['highlight'], outline='')
        
        # Draw soft glow circle
        self.avatar_canvas.create_oval(90, 40, 190, 140, fill=COLORS['secondary'], outline='', stipple='gray25')
        
        # Draw head
        self.avatar_canvas.create_oval(100, 50, 180, 130, fill=COLORS['surface'], outline=COLORS['primary'], width=2)
        
        # Draw large anime-style eyes
        # Left eye
        self.avatar_canvas.create_oval(120, 75, 135, 90, fill='white', outline=COLORS['shadow'], width=1)
        self.avatar_canvas.create_oval(123, 78, 132, 87, fill=COLORS['primary'], outline='', width=1)  # Green iris
        self.avatar_canvas.create_oval(125, 80, 130, 85, fill=COLORS['on_surface'], outline='', width=1)  # Pupil
        # Eye highlight
        self.avatar_canvas.create_oval(126, 81, 128, 83, fill=COLORS['surface'], outline='', width=1)
        
        # Right eye
        self.avatar_canvas.create_oval(145, 75, 160, 90, fill='white', outline=COLORS['shadow'], width=1)
        self.avatar_canvas.create_oval(148, 78, 157, 87, fill=COLORS['primary'], outline='', width=1)  # Green iris
        self.avatar_canvas.create_oval(150, 80, 155, 85, fill=COLORS['on_surface'], outline='', width=1)  # Pupil
        # Eye highlight
        self.avatar_canvas.create_oval(151, 81, 153, 83, fill=COLORS['surface'], outline='', width=1)
        
        # Draw soft smile
        self.avatar_canvas.create_arc(130, 95, 150, 110, start=0, extent=-180, style=tk.ARC, 
                                       outline=COLORS['accent'], width=2)
        
        # Draw modern-style hair/halo effect
        points = []
        for i in range(0, 360, 10):
            angle = math.radians(i)
            x = 140 + 50 * math.cos(angle)
            y = 90 + 50 * math.sin(angle)
            points.extend([x, y])
        
        self.avatar_canvas.create_line(points, fill=COLORS['secondary'], width=2, dash=(5, 5))
        
        # Draw name badge with modern styling
        self.avatar_canvas.create_rectangle(110, 150, 170, 170, fill=COLORS['primary'], outline=COLORS['surface'], width=1)
        self.avatar_canvas.create_text(140, 160, text="MIST", fill=COLORS['surface'], font=('Segoe UI', 12, 'bold'))
        
        # Draw status indicator
        self.avatar_canvas.create_oval(170, 120, 180, 130, fill=COLORS['accent'], outline=COLORS['surface'], width=1)
    
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
            self.chat_display.tag_configure(tag, foreground=COLORS['primary'], font=('Segoe UI', 11, 'bold'))
        else:
            tag = "user"
            self.chat_display.tag_configure(tag, foreground=COLORS['on_surface'], font=('Segoe UI', 11))
        
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
        self.status_indicator.config(text="● Online - Active")
    
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
    
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=COLORS['background'])
        
        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Add settings content
        settings_label = tk.Label(
            settings_window,
            text="Settings",
            bg=COLORS['background'],
            fg=COLORS['primary'],
            font=('Segoe UI', 16, 'bold')
        )
        settings_label.pack(pady=20)
        
        # Close button
        close_button = tk.Button(
            settings_window,
            text="Close",
            command=settings_window.destroy,
            bg=COLORS['primary'],
            fg=COLORS['surface'],
            font=('Segoe UI', 12),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=5
        )
        close_button.pack(pady=20)
    
    def run(self):
        """Start the interface"""
        self.root.mainloop()


def main():
    print("Starting Modern UI/UX Interface for MIST...")
    print("This interface features sleek design with contemporary graphics matching the theme.")
    
    app = ModernUIInterface()
    app.run()


if __name__ == "__main__":
    main()