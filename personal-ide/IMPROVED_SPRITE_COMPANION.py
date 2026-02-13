"""
Improved Sprite-Based Aware Companion Fairy Orb
Better handling of sprite display and animation
"""

import tkinter as tk
import time
import random
from PIL import Image, ImageTk


class ImprovedSpriteCompanion:
    def __init__(self):
        # Create a transparent window for the fairy orb
        self.root = tk.Tk()
        self.root.title("Improved Sprite-Based Aware Companion Fairy Orb")
        
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
        
        # Store references to prevent garbage collection
        self.sprite_images = []
        
        # Load sprites
        self.load_sprites()
        
        # Animation properties
        self.current_frame = 0
        self.animation_running = True
        
        # Interaction states
        self.interaction_state = "aware"
        
        # Start animation
        self.animate()
        
        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
        
        # Bind double-click to cycle interaction states
        self.canvas.bind("<Double-Button-1>", self.cycle_interaction_state)
    
    def load_sprites(self):
        """Load all the generated sprites"""
        try:
            # Load all animation frames
            self.animation_frames = []
            for i in range(12):  # 12 frames as generated
                try:
                    frame_img = Image.open(f"sprites/animation_frame_{i:02d}.png")
                    # Ensure the image is in RGBA mode for transparency
                    if frame_img.mode != 'RGBA':
                        frame_img = frame_img.convert('RGBA')
                    frame_photo = ImageTk.PhotoImage(frame_img)
                    self.animation_frames.append(frame_photo)
                    # Keep reference to prevent garbage collection
                    self.sprite_images.append(frame_photo)
                except FileNotFoundError:
                    print(f"Frame {i} not found, using fallback")
                    break
            
            if not self.animation_frames:
                # Create a simple fallback image
                fallback_img = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
                fallback_photo = ImageTk.PhotoImage(fallback_img)
                self.animation_frames = [fallback_photo]
                self.sprite_images.append(fallback_photo)
            
            print(f"Loaded {len(self.animation_frames)} animation frames")
            
            # Load the composite image as well
            try:
                composite_img = Image.open("sprites/composite_character.png")
                if composite_img.mode != 'RGBA':
                    composite_img = composite_img.convert('RGBA')
                self.composite_photo = ImageTk.PhotoImage(composite_img)
                self.sprite_images.append(self.composite_photo)
            except FileNotFoundError:
                print("Composite image not found")
                self.composite_photo = self.animation_frames[0] if self.animation_frames else None
                
        except Exception as e:
            print(f"Error loading sprites: {e}")
            # Create a fallback
            fallback_img = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
            fallback_photo = ImageTk.PhotoImage(fallback_img)
            self.animation_frames = [fallback_photo]
            self.sprite_images.append(fallback_photo)
    
    def animate(self):
        """Animate the fairy orb using sprite frames"""
        if self.animation_running and self.animation_frames:
            # Display current frame
            current_sprite = self.animation_frames[self.current_frame]
            # Clear canvas and draw the sprite
            self.canvas.delete("all")
            self.canvas.create_image(100, 100, image=current_sprite)
            
            # Advance to next frame
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
        
        # Schedule next frame (about 12 FPS for smooth animation)
        self.root.after(83, self.animate)  # ~12 FPS (1000ms/83ms ≈ 12)
    
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
    
    def appear(self):
        """Make the fairy orb appear"""
        self.set_interaction_state("responding", 200)
        # Visual indication only
        pass
    
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
    print("Starting Improved Sprite-Based Aware Companion Fairy Orb...")
    print("Better handling of sprite display and animation.")
    print("Features include:")
    print("- Properly loaded art sprites with transparency")
    print("- Smooth 12 FPS animation using pre-rendered frames")
    print("- All original interaction features preserved")
    print("- Better memory management to prevent garbage collection issues")
    
    orb = ImprovedSpriteCompanion()
    
    # Example: Make orb appear
    def demo_appear():
        orb.appear()
    
    # Schedule demo appearance after 2 seconds
    orb.root.after(2000, demo_appear)
    
    orb.run()


if __name__ == "__main__":
    main()