"""
Visual Companion Component for MIST Companion Intelligence
Implements the ethereal, Mars-inspired visual representation
"""

import asyncio
import math
import random
from datetime import datetime
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass, field

from integration.CORE_HUB import Message, ComponentType, CoreHub


@dataclass
class Position:
    """Represents 3D position in space"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Color:
    """Represents RGB color with alpha"""
    r: float = 1.0  # 0.0 to 1.0
    g: float = 1.0
    b: float = 1.0
    a: float = 1.0


@dataclass
class Particle:
    """Individual particle for ethereal effects"""
    position: Position
    velocity: Position
    color: Color
    size: float
    lifetime: float
    max_lifetime: float


class AnimationController:
    """Controls animations and emotional expressions"""
    
    def __init__(self):
        self.current_animation = "idle"
        self.animation_blend = 1.0  # 0.0 to 1.0
        self.emotional_state = "neutral"
        self.expression_intensity = 0.5
        self.last_update_time = datetime.now()
    
    def set_emotional_state(self, state: str, intensity: float = 0.5):
        """Set the current emotional state"""
        self.emotional_state = state
        self.expression_intensity = max(0.0, min(1.0, intensity))
        
        # Map emotional state to animations
        animation_map = {
            "joy": "happy_glow",
            "thoughtful": "contemplative_pulse",
            "concern": "gentle_attention",
            "excitement": "bright_sparkle",
            "comfort": "soothing_wave",
            "neutral": "idle_breath"
        }
        self.current_animation = animation_map.get(state, "idle_breath")
    
    def update_animation(self):
        """Update animation based on current state"""
        current_time = datetime.now()
        delta_time = (current_time - self.last_update_time).total_seconds()
        self.last_update_time = current_time
        
        # Update animation based on emotional state and time
        if self.current_animation == "idle_breath":
            # Gentle breathing motion
            breath_phase = (datetime.now().timestamp() * 0.5) % (2 * math.pi)
            self.animation_blend = 0.8 + 0.2 * math.sin(breath_phase)
        
        elif self.current_animation == "happy_glow":
            # Brighter colors when joyful
            self.animation_blend = min(1.0, self.animation_blend + 0.02)
        
        elif self.current_animation == "contemplative_pulse":
            # Slower, deeper pulses when thoughtful
            pulse_phase = (datetime.now().timestamp() * 0.3) % (2 * math.pi)
            self.animation_blend = 0.6 + 0.4 * abs(math.sin(pulse_phase / 2))
        
        elif self.current_animation == "gentle_attention":
            # Focused attention animation
            self.animation_blend = 0.9
    
    def get_animation_params(self) -> Dict[str, Any]:
        """Get parameters for current animation"""
        return {
            "animation": self.current_animation,
            "blend": self.animation_blend,
            "intensity": self.expression_intensity,
            "emotional_state": self.emotional_state
        }


class ParticleSystem:
    """Manages the ethereal particle effects around the form"""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.max_particles = 100
        self.emission_rate = 5  # particles per second
        self.base_color = Color(0.8, 0.6, 0.9, 0.7)  # Soft purplish mist
        self.mars_color = Color(0.8, 0.4, 0.4, 0.8)  # Mars red
    
    def emit_particles(self, count: int, center_pos: Position, emission_type: str = "mist"):
        """Emit new particles"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                # Remove oldest particles if at max
                self.particles.pop(0)
            
            # Random position around center
            pos = Position(
                center_pos.x + random.uniform(-0.5, 0.5),
                center_pos.y + random.uniform(-0.5, 0.5),
                center_pos.z + random.uniform(-0.5, 0.5)
            )
            
            # Random velocity
            vel = Position(
                random.uniform(-0.1, 0.1),
                random.uniform(-0.1, 0.1),
                random.uniform(-0.1, 0.1)
            )
            
            # Choose color based on emission type
            if emission_type == "mars":
                color = Color(
                    self.mars_color.r + random.uniform(-0.1, 0.1),
                    self.mars_color.g + random.uniform(-0.1, 0.1),
                    self.mars_color.b + random.uniform(-0.1, 0.1),
                    self.mars_color.a + random.uniform(-0.2, 0.2)
                )
            else:
                color = Color(
                    self.base_color.r + random.uniform(-0.1, 0.1),
                    self.base_color.g + random.uniform(-0.1, 0.1),
                    self.base_color.b + random.uniform(-0.1, 0.1),
                    self.base_color.a + random.uniform(-0.2, 0.2)
                )
            
            # Random size and lifetime
            size = random.uniform(0.05, 0.2)
            lifetime = random.uniform(2.0, 5.0)
            
            particle = Particle(pos, vel, color, size, lifetime, lifetime)
            self.particles.append(particle)
    
    def update_particles(self, delta_time: float):
        """Update all particles"""
        for particle in self.particles[:]:  # Use slice to iterate safely
            # Update position based on velocity
            particle.position.x += particle.velocity.x * delta_time * 10
            particle.position.y += particle.velocity.y * delta_time * 10
            particle.position.z += particle.velocity.z * delta_time * 10
            
            # Decrease lifetime
            particle.lifetime -= delta_time
            
            # Fade out as lifetime decreases
            age_ratio = particle.lifetime / particle.max_lifetime
            particle.color.a = particle.color.a * age_ratio if age_ratio > 0 else 0
            
            # Remove dead particles
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def get_active_particles(self) -> List[Particle]:
        """Get list of currently active particles"""
        return [p for p in self.particles if p.lifetime > 0]


class VisualForm:
    """The main visual representation of MIST"""
    
    def __init__(self):
        self.position = Position(0, 0, 0)
        self.rotation = Position(0, 0, 0)
        self.scale = 1.0
        self.opacity = 1.0
        self.color = Color(0.9, 0.8, 1.0, 0.8)  # Soft ethereal color
        self.mars_red = Color(0.8, 0.4, 0.4, 0.9)  # Mars-inspired accent
        self.base_shape = "humanoid_ether"  # ethereal humanoid form
        self.size = (0.8, 1.8, 0.4)  # width, height, depth
        self.luminosity = 0.7  # How much the form glows
    
    def update_form(self, animation_params: Dict[str, Any], mars_mentioned: bool = False):
        """Update the visual form based on animation and context"""
        # Update luminosity based on animation
        if animation_params["emotional_state"] == "joy":
            self.luminosity = min(1.0, 0.7 + animation_params["intensity"] * 0.3)
        elif animation_params["emotional_state"] == "thoughtful":
            self.luminosity = max(0.4, 0.7 - animation_params["intensity"] * 0.3)
        elif animation_params["emotional_state"] == "excitement":
            self.luminosity = 0.9
        else:
            self.luminosity = 0.7
        
        # Adjust color based on context
        if mars_mentioned:
            # Add Mars red accents when Mars is mentioned
            self.color = Color(
                0.85,  # More red
                0.7 * (1 - animation_params["intensity"]),  # Less green
                0.9 * (1 - animation_params["intensity"] * 0.3),  # Less blue
                0.8
            )
        else:
            # Normal ethereal color
            self.color = Color(
                0.9 - animation_params["intensity"] * 0.1,
                0.8 - animation_params["intensity"] * 0.1,
                1.0,
                0.8
            )
        
        # Slight scale adjustment based on emotional intensity
        self.scale = 1.0 + animation_params["intensity"] * 0.1
    
    def get_visual_attributes(self) -> Dict[str, Any]:
        """Get all visual attributes for rendering"""
        return {
            "position": (self.position.x, self.position.y, self.position.z),
            "rotation": (self.rotation.x, self.rotation.y, self.rotation.z),
            "scale": self.scale,
            "size": self.size,
            "color": (self.color.r, self.color.g, self.color.b, self.color.a),
            "opacity": self.opacity,
            "luminosity": self.luminosity,
            "shape": self.base_shape
        }


class VisualCompanion:
    """Main class for the visual companion component"""
    
    def __init__(self, hub: CoreHub):
        self.hub = hub
        self.name = "visual_companion"
        self.component_type = ComponentType.VISUAL
        self.active = True
        
        # Initialize visual components
        self.form = VisualForm()
        self.animation_controller = AnimationController()
        self.particle_system = ParticleSystem()
        
        # State tracking
        self.mars_mentioned_recently = False
        self.last_mars_mention_time = None
        self.attention_level = 0.5  # 0.0 to 1.0
        self.engagement_level = 0.5  # 0.0 to 1.0
        
        # Register with the hub
        self.hub.registry.register_component(
            self.name,
            self.handle_message,
            self.component_type
        )
        
        # Register for relevant events
        self.hub.event_coord.register_event_handler("user_attention", self.on_user_attention)
        self.hub.event_coord.register_event_handler("context_change", self.on_context_change)
        self.hub.event_coord.register_event_handler("system_wake", self.on_system_wake)
    
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        if not self.active:
            return
        
        # Process different types of messages
        if message.content.get("type") == "emotion_update":
            emotion = message.content.get("emotion", "neutral")
            intensity = message.content.get("intensity", 0.5)
            self.animation_controller.set_emotional_state(emotion, intensity)
        
        elif message.content.get("type") == "context_update":
            context = message.content.get("context", "")
            self.mars_mentioned_recently = "mars" in context.lower()
            if self.mars_mentioned_recently:
                self.last_mars_mention_time = datetime.now()
        
        elif message.content.get("type") == "attention_update":
            self.attention_level = message.content.get("level", 0.5)
        
        elif message.content.get("type") == "render_request":
            # Return current visual state
            visual_state = self.get_current_visual_state()
            response_msg = Message(
                id=f"{message.id}_response",
                source=self.name,
                destination=message.source,
                content={
                    "type": "visual_state",
                    "state": visual_state
                },
                context={"response_to": message.id}
            )
            await self.hub.send_message(response_msg)
    
    def get_current_visual_state(self) -> Dict[str, Any]:
        """Get the complete current visual state"""
        # Update animation
        self.animation_controller.update_animation()
        
        # Update form based on animation and context
        animation_params = self.animation_controller.get_animation_params()
        self.form.update_form(animation_params, self.mars_mentioned_recently)
        
        # Update particles
        current_time = datetime.now()
        delta_time = 1.0/60  # Assuming 60 FPS for particle updates
        
        # Emit particles based on emotional state
        emission_rate = int(self.animation_controller.expression_intensity * 3)
        if emission_rate > 0:
            self.particle_system.emit_particles(
                emission_rate,
                self.form.position,
                "mars" if self.mars_mentioned_recently else "mist"
            )
        
        self.particle_system.update_particles(delta_time)
        
        # Calculate if Mars is still considered mentioned recently (within 10 seconds)
        if self.last_mars_mention_time:
            if (current_time - self.last_mars_mention_time).total_seconds() > 10:
                self.mars_mentioned_recently = False
        
        return {
            "form_attributes": self.form.get_visual_attributes(),
            "animation_params": animation_params,
            "particles": [
                {
                    "position": (p.position.x, p.position.y, p.position.z),
                    "color": (p.color.r, p.color.g, p.color.b, p.color.a),
                    "size": p.size,
                    "lifetime": p.lifetime,
                    "max_lifetime": p.max_lifetime
                }
                for p in self.particle_system.get_active_particles()
            ],
            "timestamp": datetime.now().isoformat(),
            "attention_level": self.attention_level,
            "engagement_level": self.engagement_level
        }
    
    async def on_user_attention(self, event_type: str, data: Any):
        """Handle user attention events"""
        if data and "level" in data:
            self.attention_level = data["level"]
            # Adjust form opacity based on attention
            self.form.opacity = 0.5 + self.attention_level * 0.5
    
    async def on_context_change(self, event_type: str, data: Any):
        """Handle context change events"""
        if data and "context" in data:
            context_text = data["context"].lower()
            self.mars_mentioned_recently = "mars" in context_text
            if self.mars_mentioned_recently:
                self.last_mars_mention_time = datetime.now()
                # Trigger Mars-specific animation
                self.animation_controller.set_emotional_state("excitement", 0.8)
    
    async def on_system_wake(self, event_type: str, data: Any):
        """Handle system wake events"""
        # Gentle awakening animation
        self.animation_controller.set_emotional_state("neutral", 0.3)
    
    async def update_loop(self):
        """Main update loop for the visual companion"""
        while self.active:
            try:
                # Update visual state
                visual_state = self.get_current_visual_state()
                
                # Potentially send visual updates to interested components
                if random.random() < 0.1:  # Send update occasionally
                    update_msg = Message(
                        id=f"visual_update_{datetime.now().timestamp()}",
                        source=self.name,
                        destination="visualization_interface",  # UI component
                        content={
                            "type": "visual_update",
                            "state": visual_state
                        }
                    )
                    await self.hub.send_message(update_msg)
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(1/30)  # ~30 FPS
                
            except Exception as e:
                print(f"Error in visual companion update loop: {e}")
                await asyncio.sleep(1)  # Pause on error


# Example usage
async def main():
    # Initialize the core hub
    hub = CoreHub()
    await hub.start()
    
    # Create the visual companion
    visual_comp = VisualCompanion(hub)
    
    # Start the update loop in background
    update_task = asyncio.create_task(visual_comp.update_loop())
    
    # Simulate some interactions
    await asyncio.sleep(1)
    
    # Send an emotion update
    emotion_msg = Message(
        id="test_emotion_1",
        source="conversation_engine",
        destination="visual_companion",
        content={
            "type": "emotion_update",
            "emotion": "joy",
            "intensity": 0.8
        }
    )
    await hub.send_message(emotion_msg)
    
    await asyncio.sleep(2)
    
    # Send a context update mentioning Mars
    context_msg = Message(
        id="test_context_1",
        source="conversation_engine",
        destination="visual_companion",
        content={
            "type": "context_update",
            "context": "I was thinking about Mars and the red planet missions"
        }
    )
    await hub.send_message(context_msg)
    
    await asyncio.sleep(2)
    
    # Request current visual state
    render_msg = Message(
        id="request_render_1",
        source="renderer",
        destination="visual_companion",
        content={
            "type": "render_request"
        }
    )
    await hub.send_message(render_msg)
    
    # Let it run for a bit
    await asyncio.sleep(5)
    
    # Cancel the update task and shut down
    update_task.cancel()
    await hub.shutdown()


if __name__ == "__main__":
    # Uncomment to run the example
    # asyncio.run(main())
    pass