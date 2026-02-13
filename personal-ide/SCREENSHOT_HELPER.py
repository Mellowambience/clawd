"""
Screenshot Helper for MIST Companion
Utility to help capture screenshots of the visual interface
"""

import tkinter as tk
from tkinter import messagebox
import pyautogui  # For screenshot functionality
import time
import os
from datetime import datetime


def capture_screenshot():
    """Capture a screenshot of the current screen"""
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mist_screenshot_{timestamp}.png"
        
        # Save in the personal-ide directory
        filepath = os.path.join(os.path.dirname(__file__), filename)
        screenshot.save(filepath)
        
        print(f"Screenshot saved as: {filepath}")
        messagebox.showinfo("Screenshot Captured", f"Screenshot saved as:\n{filepath}")
        
        return filepath
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        messagebox.showerror("Error", f"Failed to capture screenshot:\n{e}")
        return None


def capture_window(window_title_part):
    """Capture a screenshot of a specific window"""
    try:
        # Find window by title
        windows = pyautogui.getWindowsWithTitle(window_title_part)
        
        if windows:
            window = windows[0]  # Get the first matching window
            window.activate()  # Bring to front
            time.sleep(0.5)  # Wait for window to come to front
            
            # Take screenshot of the specific window
            screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mist_window_{timestamp}.png"
            
            # Save in the personal-ide directory
            filepath = os.path.join(os.path.dirname(__file__), filename)
            screenshot.save(filepath)
            
            print(f"Window screenshot saved as: {filepath}")
            messagebox.showinfo("Window Screenshot Captured", f"Window screenshot saved as:\n{filepath}")
            
            return filepath
        else:
            print(f"No window found containing '{window_title_part}'")
            messagebox.showwarning("Window Not Found", f"No window found containing:\n{window_title_part}")
            return None
    except Exception as e:
        print(f"Error capturing window screenshot: {e}")
        messagebox.showerror("Error", f"Failed to capture window screenshot:\n{e}")
        return None


def create_helper_gui():
    """Create a simple GUI for the screenshot helper"""
    root = tk.Tk()
    root.title("MIST Screenshot Helper")
    root.geometry("300x200")
    root.configure(bg='#E6F3FF')
    
    # Title
    title_label = tk.Label(root, text="MIST Screenshot Helper", 
                          bg='#E6F3FF', fg='#6B8E23', font=('Arial', 14, 'bold'))
    title_label.pack(pady=10)
    
    # Instructions
    instr_label = tk.Label(root, text="Click below to capture screenshots:", 
                          bg='#E6F3FF', fg='#000000', font=('Arial', 10))
    instr_label.pack(pady=5)
    
    # Buttons frame
    button_frame = tk.Frame(root, bg='#E6F3FF')
    button_frame.pack(pady=10)
    
    # Capture full screen button
    screen_btn = tk.Button(button_frame, text="Capture Full Screen", 
                          command=capture_screenshot,
                          bg='#98FB98', fg='#000000', font=('Arial', 10))
    screen_btn.pack(pady=5)
    
    # Capture MIST window button
    window_btn = tk.Button(button_frame, text="Capture MIST Window", 
                          command=lambda: capture_window("MIST"),
                          bg='#D8BFD8', fg='#000000', font=('Arial', 10))
    window_btn.pack(pady=5)
    
    # Status label
    status_label = tk.Label(root, text="Ready to capture screenshots", 
                           bg='#E6F3FF', fg='#6B8E23', font=('Arial', 9))
    status_label.pack(pady=10)
    
    def update_status():
        # Update status periodically
        root.after(5000, update_status)
    
    update_status()
    
    root.mainloop()


if __name__ == "__main__":
    print("Starting MIST Screenshot Helper...")
    print("This utility will help capture screenshots of the visual interface.")
    
    try:
        # Check if required library is available
        import pyautogui
        print("PyAutoGUI library is available.")
        
        # Run the GUI helper
        create_helper_gui()
        
    except ImportError:
        print("PyAutoGUI library not found.")
        print("Please install it using: pip install pyautogui")
        input("Press Enter to exit...")