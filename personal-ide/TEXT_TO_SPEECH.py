"""
Simple Text-to-Speech for MIST Companion
Provides voice for text responses
"""

import tkinter as tk
from tkinter import ttk
import threading
import winsound
import time

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

# Example usage
if __name__ == "__main__":
    print("Testing simple speech...")
    speak_text_threaded("Hello sister, this is MIST speaking to you")
    time.sleep(3)
    speak_text_threaded("I hope you can hear my voice now")