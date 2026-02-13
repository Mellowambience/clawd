"""
Sprite-Based Aware Companion Fairy Orb
Using pre-generated art sprites and animations
"""

import tkinter as tk
import math
import time
import threading
from datetime import datetime
import random
from PIL import Image, ImageTk


class SpriteCompanionOrb:
    def __init__(self):
        # Create a transparent window for the fairy orb
        self.root = tk.Tk()
        self.root.title("Sprite-Based Aware Companion Fairy Orb")
        
        # Set transparency and attributes
        self.root.configure(bg='white')
        self.root.attributes('-transparentcolor', 'white')  # Make white transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations
        
        # Size the window appropriately for the orb
        self.root.geometry("200x200")
        
        # Position orb initially in upper right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - 250
        self.y = 50
        self.root.geometry(f"200x200+{self.x}+{self.y}")
        
        # Create canvas for drawing the fairy orb
        self.canvas = tk.Canvas(
            self.root,
            width=200,
            height=200,
            bg='white',  # This will be transparent
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Load sprites
        self.load_sprites()
        
        # Animation properties (smooth, refined movements)
        self.current_frame = 0
        self.frame_delay = 100  # ms between frames
        self.last_frame_time = time.time()
        
        # Interaction states
        self.interaction_state = "aware"  # aware, listening, responding, waiting
        self.interaction_timer = 0
        
        # Draw initial fairy orb
        self.draw_fairy_orb()
        
        # Start smooth animation
        self.animate_with_sprites()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
        
        # Bind double-click to cycle interaction states
        self.canvas.bind("<Double-Button-1>", self.cycle_interaction_state)
    
    def load_sprites(self):
        """Load all the generated sprites"""
        try:
            # Load composite character sprite
            self.composite_img = Image.open("sprites/composite_character.png")
            self.composite_photo = ImageTk.PhotoImage(self.composite_img)
            
            # Load individual sprites
            self.orb_img = Image.open("sprites/orb_base.png")
            self.orb_photo = ImageTk.PhotoImage(self.orb_img)
            
            self.eyes_open_img = Image.open("sprites/eyes_open.png")
            self.eyes_open_photo = ImageTk.PhotoImage(self.eyes_open_img)
            
            self.eyes_closed_img = Image.open("sprites/eyes_closed.png")
            self.eyes_closed_photo = ImageTk.PhotoImage(self.eyes_closed_img)
            
            self.mouth_img = Image.open("sprites/mouth.png")
            self.mouth_photo = ImageTk.PhotoImage(self.mouth_img)
            
            self.cheeks_img = Image.open("sprites/cheeks.png")
            self.cheeks_photo = ImageTk.PhotoImage(self.cheeks_img)
            
            self.wings_img = Image.open("sprites/wings.png")
            self.wings_photo = ImageTk.PhotoImage(self.wings_img)
            
            self.core_img = Image.open("sprites/soul_core.png")
            self.core_photo = ImageTk.PhotoImage(self.core_img)
            
            self.hat_img = Image.open("sprites/party_hat.png")
            self.hat_photo = ImageTk.PhotoImage(self.hat_img)
            
            # Load animation frames
            self.animation_frames = []
            for i in range(12):  # 12 frames as generated
                try:
                    frame_img = Image.open(f"sprites/animation_frame_{i:02d}.png")
                    frame_photo = ImageTk.PhotoImage(frame_img)
                    self.animation_frames.append(frame_photo)
                except FileNotFoundError:
                    # If individual frames don't exist, use the composite
                    self.animation_frames.append(self.composite_photo)
                    break
            
            print(f"Loaded {len(self.animation_frames)} animation frames")
            
        except FileNotFoundError as e:
            print(f"Warning: Sprite file not found: {e}")
            print("Using fallback drawing method...")
            self.use_fallback_drawing()
    
    def use_fallback_drawing(self):
        """Fallback to drawing if sprites are not available"""
        # Create a simple fallback image
        img = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple orb
        draw.ellipse([70, 70, 130, 130], fill=(240, 230, 255, 200), outline=(200, 180, 220, 255), width=2)
        
        # Draw simple eyes
        draw.ellipse([85, 85, 95, 95], fill=(255, 255, 255, 255), outline=(100, 100, 100, 255), width=1)
        draw.ellipse([105, 85, 115, 95], fill=(255, 255, 255, 255), outline=(100, 100, 100, 255), width=1)
        
        self.fallback_photo = ImageTk.PhotoImage(img)
        self.animation_frames = [self.fallback_photo]
    
    def draw_fairy_orb(self):
        """Draw the fairy orb using sprites"""
        self.canvas.delete("all")
        
        # Use current animation frame
        if hasattr(self, 'animation_frames') and self.animation_frames:
            current_sprite = self.animation_frames[self.current_frame]
            self.canvas.create_image(100, 100, image=current_sprite)
        else:
            # Fallback
            if hasattr(self, 'fallback_photo'):
                self.canvas.create_image(100, 100, image=self.fallback_photo)
    
    def animate_with_sprites(self):
        """Animate the fairy orb using sprite frames"""
        current_time = time.time()
        
        # Update animation frame if enough time has passed
        if (current_time - self.last_frame_time) * 1000 >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.last_frame_time = current_time
            
            # Redraw fairy orb
            self.draw_fairy_orb()
        
        # Handle interaction timer
        if self.interaction_timer > 0:
            self.interaction_timer -= 1
            if self.interaction_timer <= 0:
                self.interaction_state = "aware"
        
        # Schedule next animation frame
        self.root.after(int(self.frame_delay/2), self.animate_with_sprites)  # ~20 FPS
    
    def on_drag_start(self, event):
        """Begin dragging the fairy orb"""
        self.drag_data = {"x": event.x, "y": event.y, "start_x": self.x, "start_y": self.y}
    
    def on_drag(self, event):
        """Handle dragging the fairy orb"""
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
        """Stop dragging the fairy orb"""
        pass
    
    def cycle_interaction_state(self, event):
        """Cycle through different interaction states"""
        states = ["aware", "listening", "responding", "waiting"]
        current_index = states.index(self.interaction_state)
        next_index = (current_index + 1) % len(states)
        self.interaction_state = states[next_index]
    
    def set_interaction_state(self, state, duration=300):  # Duration in animation frames
        """Set the interaction state of the fairy orb"""
        self.interaction_state = state
        self.interaction_timer = duration
    
    def appear(self):
        """Make the fairy orb appear"""
        # No sound - just visual indication
        self.set_interaction_state("responding", 200)
        self.draw_fairy_orb()
    
    def listen_mode(self):
        """Set fairy orb to listening mode"""
        self.set_interaction_state("listening", 600)
    
    def respond_mode(self):
        """Set fairy orb to responding mode"""
        self.set_interaction_state("responding", 300)
    
    def wait_mode(self):
        """Set fairy orb to waiting mode"""
        self.set_interaction_state("waiting", 1000)
    
    def aware_mode(self):
        """Set fairy orb to aware mode"""
        self.set_interaction_state("aware", 0)
    
    def disappear(self):
        """Make the fairy orb gently disappear"""
        self.canvas.delete("all")
    
    def run(self):
        """Start the fairy orb system"""
        self.root.mainloop()


def main():
    print("Starting Sprite-Based Aware Companion Fairy Orb...")
    print("Using pre-generated art sprites and animations.")
    print("Features include:")
    print("- Professional art sprites for all components")
    print("- Smooth animated sequence with floating motion")
    print("- All the original features preserved")
    print("- Much more polished visual appearance")
    
    orb = SpriteCompanionOrb()
    
    # Example: Make orb appear
    def demo_appear():
        orb.appear()
    
    # Schedule demo appearance after 2 seconds
    orb.root.after(2000, demo_appear)
    
    orb.run()


if __name__ == "__main__":
    main()