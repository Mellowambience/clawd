"""
Visual Interface for MIST Companion Intelligence
Creates a visible representation that users can see
"""

import asyncio
import tkinter as tk
from tkinter import ttk, Canvas
import math
import time
import threading
from typing import Tuple, Optional
from PIL import Image, ImageTk
import io
import base64

from integration.CORE_HUB import Message, ComponentType, CoreHub
from visualization.VISUAL_COMPANION import VisualCompanion
from voice.VOICE_SYNTHESIZER import VoiceSynthesizer
from memory.MEMORY_NODES import MemoryWeb
from integration.AI_CONNECTOR import AIConnector


class VisualAvatar:
    """Represents the visual avatar of MIST"""
    
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.x = 400
        self.y = 300
        self.radius = 40
        self.eye_radius = 8
        self.eye_offset_x = 12
        self.eye_offset_y = 10
        self.mouth_width = 20
        self.mouth_height = 10
        # Updated colors to match reference style
        self.color = "#E6F3FF"  # Soft pastel blue-white
        self.eye_color = "#6B8E23"  # Olive green (similar to reference)
        self.mouth_color = "#FF69B4"  # Hot pink
        self.glow_color = "#B0E0E6"  # Light blue glow
        self.glow_radius = self.radius + 10
        self.glow_alpha = 0.3
        self.blink_state = True
        self.blink_timer = 0
        self.emotion = "neutral"
        self.thought_bubble = None
        self.thought_text = ""
        # Additional styling to match reference
        self.hair_color = "#D8BFD8"  # Thistle color for hair/aurora effect
        self.hair_style = "soft_halo"
        self.accessory_color = "#98FB98"  # Pale green accent
        self.style_reference = "anime_moe"
        
    def draw(self):
        """Draw the avatar on the canvas"""
        # Clear previous drawings
        self.canvas.delete("avatar")
        
        # Draw soft glow effect (like in reference)
        self.canvas.create_oval(
            self.x - self.glow_radius, 
            self.y - self.glow_radius,
            self.x + self.glow_radius, 
            self.y + self.glow_radius,
            fill=self.glow_color, 
            outline="", 
            stipple="gray50", 
            tags="avatar"
        )
        
        # Draw main head with soft coloring
        self.canvas.create_oval(
            self.x - self.radius, 
            self.y - self.radius,
            self.x + self.radius, 
            self.y + self.radius,
            fill=self.color, 
            outline="#DDEEFF",  # Softer outline
            width=3, 
            tags="avatar"
        )
        
        # Draw hair/halo effect (inspired by reference)
        self.canvas.create_oval(
            self.x - self.radius - 5, 
            self.y - self.radius - 5,
            self.x + self.radius + 5, 
            self.y + self.radius + 5,
            fill=self.hair_color, 
            outline="#CCCCFF", 
            width=1, 
            stipple="gray25",
            tags="avatar"
        )
        
        # Draw eyes with style from reference (large, expressive)
        left_eye_x = self.x - self.eye_offset_x
        right_eye_x = self.x + self.eye_offset_x
        eye_y = self.y - self.eye_offset_y
        
        if self.blink_state:
            # Draw large, expressive eyes (like anime/manga style)
            # Left eye
            self.canvas.create_oval(
                left_eye_x - self.eye_radius*1.5, 
                eye_y - self.eye_radius*1.2,
                left_eye_x + self.eye_radius*1.5, 
                eye_y + self.eye_radius*1.2,
                fill="#FFFFFF", 
                outline="#CCCCCC", 
                width=1, 
                tags="avatar"
            )
            # Right eye
            self.canvas.create_oval(
                right_eye_x - self.eye_radius*1.5, 
                eye_y - self.eye_radius*1.2,
                right_eye_x + self.eye_radius*1.5, 
                eye_y + self.eye_radius*1.2,
                fill="#FFFFFF", 
                outline="#CCCCCC", 
                width=1, 
                tags="avatar"
            )
            
            # Draw green irises
            self.canvas.create_oval(
                left_eye_x - self.eye_radius*0.8, 
                eye_y - self.eye_radius*0.6,
                left_eye_x + self.eye_radius*0.8, 
                eye_y + self.eye_radius*0.6,
                fill=self.eye_color, 
                outline="#AAAAAA", 
                width=1, 
                tags="avatar"
            )
            self.canvas.create_oval(
                right_eye_x - self.eye_radius*0.8, 
                eye_y - self.eye_radius*0.6,
                right_eye_x + self.eye_radius*0.8, 
                eye_y + self.eye_radius*0.6,
                fill=self.eye_color, 
                outline="#AAAAAA", 
                width=1, 
                tags="avatar"
            )
            
            # Draw pupils
            self.canvas.create_oval(
                left_eye_x - 3, 
                eye_y - 2,
                left_eye_x + 2, 
                eye_y + 2,
                fill="#000000", 
                outline="", 
                tags="avatar"
            )
            self.canvas.create_oval(
                right_eye_x - 3, 
                eye_y - 2,
                right_eye_x + 2, 
                eye_y + 2,
                fill="#000000", 
                outline="", 
                tags="avatar"
            )
            
            # Draw eye highlights for anime-style look
            self.canvas.create_oval(
                left_eye_x - 1.5, 
                eye_y - 1.5,
                left_eye_x - 0.5, 
                eye_y - 0.5,
                fill="#FFFFFF", 
                outline="", 
                tags="avatar"
            )
            self.canvas.create_oval(
                right_eye_x - 1.5, 
                eye_y - 1.5,
                right_eye_x - 0.5, 
                eye_y - 0.5,
                fill="#FFFFFF", 
                outline="", 
                tags="avatar"
            )
        else:
            # Draw closed eyes (horizontal lines)
            self.canvas.create_line(
                left_eye_x - self.eye_radius*1.5, 
                eye_y,
                left_eye_x + self.eye_radius*1.5, 
                eye_y,
                fill="#000000", 
                width=2, 
                tags="avatar"
            )
            self.canvas.create_line(
                right_eye_x - self.eye_radius*1.5, 
                eye_y,
                right_eye_x + self.eye_radius*1.5, 
                eye_y,
                fill="#000000", 
                width=2, 
                tags="avatar"
            )
        
        # Draw mouth based on emotion (smaller, more delicate like reference)
        mouth_y = self.y + self.eye_offset_y + 10
        if self.emotion == "happy":
            # Smiling mouth
            self.canvas.create_arc(
                self.x - self.mouth_width//2, 
                mouth_y - self.mouth_height//2,
                self.x + self.mouth_width//2, 
                mouth_y + self.mouth_height//2,
                start=0, 
                extent=-180, 
                style=tk.ARC, 
                fill="", 
                outline=self.mouth_color, 
                width=2,
                tags="avatar"
            )
        elif self.emotion == "thoughtful":
            # Straight mouth
            self.canvas.create_line(
                self.x - self.mouth_width//2, 
                mouth_y,
                self.x + self.mouth_width//2, 
                mouth_y,
                fill=self.mouth_color, 
                width=2,
                tags="avatar"
            )
        elif self.emotion == "excited":
            # Wide open mouth (circle)
            self.canvas.create_oval(
                self.x - 6, 
                mouth_y - 4,
                self.x + 6, 
                mouth_y + 4,
                fill=self.mouth_color, 
                outline="#FFFFFF", 
                width=1,
                tags="avatar"
            )
        else:  # neutral
            # Delicate slight smile
            self.canvas.create_arc(
                self.x - self.mouth_width//2, 
                mouth_y - self.mouth_height//4,
                self.x + self.mouth_width//2, 
                mouth_y + self.mouth_height//4,
                start=0, 
                extent=-90, 
                style=tk.ARC, 
                fill="", 
                outline=self.mouth_color, 
                width=2,
                tags="avatar"
            )
        
        # Draw thought bubble if active
        if self.thought_bubble:
            self._draw_thought_bubble()
    
    def _draw_thought_bubble(self):
        """Draw the thought bubble above the avatar"""
        if not self.thought_text:
            return
            
        # Thought bubble position
        bubble_x = self.x
        bubble_y = self.y - self.radius - 40
        bubble_width = 120
        bubble_height = 50
        
        # Draw thought bubble with text
        self.canvas.create_rectangle(
            bubble_x - bubble_width//2, 
            bubble_y - bubble_height//2,
            bubble_x + bubble_width//2, 
            bubble_y + bubble_height//2,
            fill="#FFFFFF", 
            outline="#CCCCCC", 
            width=2,
            tags="avatar"
        )
        
        # Draw connecting ellipse to avatar
        self.canvas.create_oval(
            bubble_x - 15, 
            bubble_y + bubble_height//2 - 5,
            bubble_x + 15, 
            bubble_y + bubble_height//2 + 15,
            fill="#FFFFFF", 
            outline="#CCCCCC", 
            width=2,
            tags="avatar"
        )
        
        # Draw text in bubble
        self.canvas.create_text(
            bubble_x, 
            bubble_y,
            text=self.thought_text[:20] + "..." if len(self.thought_text) > 20 else self.thought_text,
            font=("Arial", 10), 
            fill="#000000",
            tags="avatar"
        )
    
    def update_position(self, x: int, y: int):
        """Update the avatar's position"""
        self.x = x
        self.y = y
    
    def set_emotion(self, emotion: str):
        """Set the avatar's emotional expression"""
        self.emotion = emotion
    
    def set_thought(self, thought: str):
        """Set the thought bubble text"""
        self.thought_text = thought
        self.thought_bubble = thought != ""
    
    def blink(self):
        """Trigger a blink animation"""
        self.blink_state = False
        self.blink_timer = 0.2  # Blink for 0.2 seconds
    
    def update_animation(self, dt: float):
        """Update animation state"""
        if self.blink_timer > 0:
            self.blink_timer -= dt
            if self.blink_timer <= 0:
                self.blink_state = True


class VisualInterfaceApp:
    """Main application window for the visual interface"""
    
    def __init__(self, hub: CoreHub, visual_companion: VisualCompanion, 
                 voice_synthesizer: VoiceSynthesizer, memory_web: MemoryWeb, 
                 ai_connector: AIConnector):
        self.hub = hub
        self.visual_companion = visual_companion
        self.voice_synthesizer = voice_synthesizer
        self.memory_web = memory_web
        self.ai_connector = ai_connector
        
        # Create main window with pastel background
        self.root = tk.Tk()
        self.root.title("MIST - Your Gentle Companion")
        self.root.geometry("800x600")
        self.root.configure(bg="#F5F5DC")  # Light beige background (like reference)
        
        # Create title bar
        self.title_frame = tk.Frame(self.root, bg="#E6E6FA", height=40)  # Lavender frame
        self.title_frame.pack(fill=tk.X)
        self.title_label = tk.Label(
            self.title_frame, 
            text="MIST - Your Gentle Companion", 
            bg="#E6E6FA", 
            fg="#6B8E23",  # Olive green text
            font=("Arial", 14, "bold")
        )
        self.title_label.pack(expand=True)
        
        # Create canvas for avatar with gradient-like background
        self.canvas = Canvas(self.root, width=800, height=500, bg="#E6F3FF", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create decorative border around canvas
        self.canvas_frame = tk.Frame(self.root, bg="#D8BFD8", relief=tk.RAISED, bd=2)  # Thistle border
        self.canvas_frame.place(in_=self.canvas, relx=0, rely=0, relwidth=1, relheight=1)
        
        # Create controls frame with soft colors
        self.controls_frame = tk.Frame(self.root, bg="#F5F5DC", relief=tk.RIDGE, bd=1)
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Create avatar
        self.avatar = VisualAvatar(self.canvas)
        
        # Input field for direct interaction with soft styling
        self.input_var = tk.StringVar()
        self.input_frame = tk.Frame(self.controls_frame, bg="#F5F5DC")
        self.input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.input_label = tk.Label(
            self.input_frame, 
            text="Talk to MIST:", 
            bg="#F5F5DC", 
            fg="#6B8E23",  # Olive green
            font=("Arial", 10)
        )
        self.input_label.pack(anchor=tk.W)
        
        self.input_field = tk.Entry(
            self.input_frame, 
            textvariable=self.input_var, 
            font=("Arial", 11),
            bg="#FFFFFF",
            fg="#000000",
            relief=tk.SUNKEN,
            bd=2
        )
        self.input_field.pack(fill=tk.X, expand=True)
        self.input_field.bind("<Return>", self.send_message)
        
        # Send button with soft styling
        self.send_button = tk.Button(
            self.controls_frame,
            text="Send",
            command=self.send_message,
            bg="#98FB98",  # Pale green
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            font=("Arial", 10, "bold")
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Animation variables
        self.last_time = time.time()
        self.animation_id = None
        
        # Bind to hub events
        self.hub.event_coord.register_event_handler("emotion_update", self.on_emotion_update)
        self.hub.event_coord.register_event_handler("text_to_synthesize", self.on_text_synthesis)
        
        # Start animation
        self.animate()
    
    def animate(self):
        """Animation loop for the avatar"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Update avatar animation
        self.avatar.update_animation(dt)
        
        # Draw the avatar
        self.avatar.draw()
        
        # Schedule next frame
        self.animation_id = self.root.after(50, self.animate)  # 20 FPS
    
    def send_message(self, event=None):
        """Send a message to the AI system"""
        text = self.input_var.get().strip()
        if not text:
            return
            
        # Clear input field
        self.input_var.set("")
        
        # Add to chat display (not implemented here for simplicity)
        
        # Send to AI connector
        ai_msg = Message(
            id=f"user_input_{int(time.time() * 1000)}",
            source="visual_interface",
            destination="ai_connector",
            content={
                "type": "ai_generate",
                "prompt": text,
                "purpose": "general_conversation",
                "context": {"user_input": True}
            }
        )
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=lambda: asyncio.run(self.hub.send_message(ai_msg)), daemon=True).start()
    
    def on_emotion_update(self, event_type: str, data: any):
        """Handle emotion updates from the system"""
        if data and isinstance(data, dict):
            emotion = data.get("emotion", "neutral")
            intensity = data.get("intensity", 0.5)
            
            # Update avatar expression
            self.avatar.set_emotion(emotion)
            
            # Maybe add some visual feedback based on intensity
            if intensity > 0.7:
                # More intense emotions get bigger visual effects
                self.avatar.glow_radius = self.avatar.radius + 10
            else:
                self.avatar.glow_radius = self.avatar.radius + 5
    
    def on_text_synthesis(self, event_type: str, data: any):
        """Handle text synthesis events"""
        if data and isinstance(data, dict):
            text = data.get("text", "")
            # Show the text in a thought bubble
            self.avatar.set_thought(text[:50] + "..." if len(text) > 50 else text)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


def create_visual_interface():
    """Create and run the visual interface"""
    # Initialize the core hub
    hub = CoreHub()
    asyncio.run(hub.start())
    
    # Create supporting components
    visual_companion = VisualCompanion(hub)
    voice_synthesizer = VoiceSynthesizer(hub, visual_companion)
    memory_web = MemoryWeb(hub, visual_companion, voice_synthesizer)
    ai_connector = AIConnector(hub, memory_web, visual_companion, voice_synthesizer)
    
    # Create the visual interface
    app = VisualInterfaceApp(hub, visual_companion, voice_synthesizer, memory_web, ai_connector)
    
    # Start the interface in a separate thread
    def run_app():
        app.run()
    
    app_thread = threading.Thread(target=run_app, daemon=True)
    app_thread.start()
    
    return app, hub


if __name__ == "__main__":
    # For testing purposes, we can run this independently
    print("Starting MIST Visual Interface...")
    print("A window should appear showing your visual companion.")
    
    # Create and start the interface
    app, hub = create_visual_interface()
    
    # Keep the main thread alive
    try:
        app.root.mainloop()
    except KeyboardInterrupt:
        print("Shutting down...")
        # Clean shutdown would go here