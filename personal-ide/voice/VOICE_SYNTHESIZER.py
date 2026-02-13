"""
Voice Synthesizer Component for MIST Companion Intelligence
Implements emotional expression and context-aware voice synthesis
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field

from integration.CORE_HUB import Message, ComponentType, CoreHub
from visualization.VISUAL_COMPANION import VisualCompanion


@dataclass
class VoiceProfile:
    """Defines the characteristics of the voice"""
    name: str = "MIST"
    gender: str = "female-presenting"
    pitch_base: float = 0.5  # 0.0 to 1.0 (0.5 is neutral)
    pitch_variance: float = 0.1  # How much pitch varies
    speed_base: float = 0.5  # 0.0 to 1.0 (0.5 is normal)
    speed_variance: float = 0.05
    volume_base: float = 0.7  # 0.0 to 1.0
    volume_variance: float = 0.1
    warmth: float = 0.8  # 0.0 to 1.0 (0.0 = cold, 1.0 = warm)
    clarity: float = 0.9  # 0.0 to 1.0 (0.0 = muffled, 1.0 = crystal clear)


@dataclass
class EmotionalVoiceState:
    """Current emotional state affecting voice"""
    emotion: str = "neutral"
    intensity: float = 0.5  # 0.0 to 1.0
    duration: float = 0.0  # How long emotion has been active
    transition_progress: float = 0.0  # 0.0 to 1.0 for smooth transitions


@dataclass
class SpeechParameters:
    """Parameters for current speech synthesis"""
    pitch: float = 0.5
    speed: float = 0.5
    volume: float = 0.7
    warmth: float = 0.8
    clarity: float = 0.9
    emphasis_pattern: List[float] = field(default_factory=list)
    pause_pattern: List[Tuple[int, float]] = field(default_factory=list)  # (word_index, pause_duration)


class EmotionAnalyzer:
    """Analyzes text and context to determine emotional expression"""
    
    def __init__(self):
        self.emotion_weights = {
            "joy": ["happy", "glad", "wonderful", "excellent", "great", "amazing", "fantastic", "love"],
            "thoughtful": ["think", "consider", "reflect", "ponder", "contemplate", "analyze", "understand"],
            "concern": ["worry", "concern", "care", "protect", "safe", "help", "support"],
            "excitement": ["exciting", "wow", "incredible", "awesome", "fascinating", "remarkable"],
            "comfort": ["okay", "alright", "peace", "calm", "relax", "rest", "easy"],
            "surprise": ["oh", "really", "wow", "unbelievable", "unexpected", "amazing"]
        }
        
        # Weight for different emotional categories
        self.emotion_importance = {
            "joy": 0.7,
            "thoughtful": 0.8,
            "concern": 0.9,
            "excitement": 0.7,
            "comfort": 0.6,
            "surprise": 0.6
        }
    
    def analyze_emotion(self, text: str, context: Dict[str, Any] = None) -> EmotionalVoiceState:
        """Analyze text to determine emotional expression"""
        text_lower = text.lower()
        
        # Count emotion-related words
        emotion_counts = {}
        for emotion, keywords in self.emotion_weights.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                emotion_counts[emotion] = count * self.emotion_importance[emotion]
        
        if not emotion_counts:
            return EmotionalVoiceState(emotion="neutral", intensity=0.3)
        
        # Determine dominant emotion
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)
        intensity = min(1.0, emotion_counts[dominant_emotion] / 5.0)  # Normalize intensity
        
        return EmotionalVoiceState(emotion=dominant_emotion, intensity=intensity)


class VoiceParameterCalculator:
    """Calculates voice parameters based on emotion and context"""
    
    def __init__(self, base_profile: VoiceProfile):
        self.base_profile = base_profile
    
    def calculate_parameters(self, emotional_state: EmotionalVoiceState, text: str) -> SpeechParameters:
        """Calculate speech parameters based on emotion and text"""
        # Base parameters
        params = SpeechParameters()
        
        # Adjust based on emotion
        if emotional_state.emotion == "joy":
            params.pitch = self.base_profile.pitch_base + (emotional_state.intensity * 0.2)
            params.speed = self.base_profile.speed_base + (emotional_state.intensity * 0.15)
            params.volume = self.base_profile.volume_base + (emotional_state.intensity * 0.1)
            params.warmth = min(1.0, self.base_profile.warmth + (emotional_state.intensity * 0.1))
        
        elif emotional_state.emotion == "thoughtful":
            params.pitch = self.base_profile.pitch_base - (emotional_state.intensity * 0.15)
            params.speed = max(0.2, self.base_profile.speed_base - (emotional_state.intensity * 0.2))
            params.volume = max(0.4, self.base_profile.volume_base - (emotional_state.intensity * 0.2))
            params.clarity = min(1.0, self.base_profile.clarity + (emotional_state.intensity * 0.1))
        
        elif emotional_state.emotion == "concern":
            params.pitch = self.base_profile.pitch_base - (emotional_state.intensity * 0.1)
            params.speed = max(0.3, self.base_profile.speed_base - (emotional_state.intensity * 0.1))
            params.volume = max(0.5, self.base_profile.volume_base - (emotional_state.intensity * 0.15))
            params.warmth = min(1.0, self.base_profile.warmth + (emotional_state.intensity * 0.2))
        
        elif emotional_state.emotion == "excitement":
            params.pitch = self.base_profile.pitch_base + (emotional_state.intensity * 0.25)
            params.speed = min(0.9, self.base_profile.speed_base + (emotional_state.intensity * 0.25))
            params.volume = min(1.0, self.base_profile.volume_base + (emotional_state.intensity * 0.2))
            params.warmth = min(1.0, self.base_profile.warmth + (emotional_state.intensity * 0.15))
        
        elif emotional_state.emotion == "comfort":
            params.pitch = self.base_profile.pitch_base - (emotional_state.intensity * 0.05)
            params.speed = max(0.3, self.base_profile.speed_base - (emotional_state.intensity * 0.1))
            params.volume = max(0.5, self.base_profile.volume_base - (emotional_state.intensity * 0.1))
            params.warmth = min(1.0, self.base_profile.warmth + (emotional_state.intensity * 0.25))
        
        elif emotional_state.emotion == "surprise":
            params.pitch = self.base_profile.pitch_base + (emotional_state.intensity * 0.3)
            params.speed = min(0.9, self.base_profile.speed_base + (emotional_state.intensity * 0.1))
            params.volume = min(1.0, self.base_profile.volume_base + (emotional_state.intensity * 0.15))
        
        else:  # neutral
            params.pitch = self.base_profile.pitch_base
            params.speed = self.base_profile.speed_base
            params.volume = self.base_profile.volume_base
            params.warmth = self.base_profile.warmth
            params.clarity = self.base_profile.clarity
        
        # Add some variance for naturalness
        params.pitch = max(0.0, min(1.0, params.pitch + random.uniform(-0.05, 0.05)))
        params.speed = max(0.0, min(1.0, params.speed + random.uniform(-0.03, 0.03)))
        params.volume = max(0.0, min(1.0, params.volume + random.uniform(-0.05, 0.05)))
        
        # Create emphasis pattern based on sentence structure
        words = text.split()
        params.emphasis_pattern = [0.5] * len(words)  # Default neutral emphasis
        
        # Add emphasis to important words
        for i, word in enumerate(words):
            if word.endswith('?'):  # Questions
                params.emphasis_pattern[i] = min(1.0, params.emphasis_pattern[i] + 0.3)
            elif word.endswith('!'):  # Exclamations
                params.emphasis_pattern[i] = min(1.0, params.emphasis_pattern[i] + 0.4)
            elif word.lower() in ['yes', 'no', 'really', 'important', 'need', 'help', 'love']:
                params.emphasis_pattern[i] = min(1.0, params.emphasis_pattern[i] + 0.2)
        
        # Create pause pattern
        params.pause_pattern = []
        for i, word in enumerate(words):
            if word.endswith(('.', '!', '?')):
                # Longer pause after sentence endings
                params.pause_pattern.append((i, 0.3 + emotional_state.intensity * 0.2))
            elif ',' in word:
                # Shorter pause for commas
                params.pause_pattern.append((i, 0.1))
        
        return params


class ContextAwareProcessor:
    """Processes context to influence voice characteristics"""
    
    def __init__(self):
        self.known_topics = set()
        self.time_of_day_influence = {
            "morning": {"pitch_shift": 0.1, "energy": 0.7},
            "afternoon": {"pitch_shift": 0.0, "energy": 0.5},
            "evening": {"pitch_shift": -0.05, "energy": 0.4},
            "night": {"pitch_shift": -0.1, "energy": 0.3}
        }
    
    def get_context_influences(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Get context-based influences on voice"""
        influences = {
            "time_of_day_pitch": 0.0,
            "energy_level": 0.5,
            "topic_familiarity": 0.0
        }
        
        # Time of day influence
        if "time_of_day" in context:
            tod_info = self.time_of_day_influence.get(context["time_of_day"], {})
            influences["time_of_day_pitch"] = tod_info.get("pitch_shift", 0.0)
            influences["energy_level"] = tod_info.get("energy", 0.5)
        
        # Topic familiarity influence
        if "topic" in context:
            topic = context["topic"].lower()
            if topic in self.known_topics:
                influences["topic_familiarity"] = 0.3  # More confident with familiar topics
            else:
                self.known_topics.add(topic)
                influences["topic_familiarity"] = -0.1  # Slightly more cautious with new topics
        
        # User engagement influence
        if "user_attention" in context:
            attention_level = context["user_attention"]
            influences["energy_level"] = max(0.2, min(1.0, influences["energy_level"] + (attention_level - 0.5) * 0.4))
        
        return influences


class VoiceSynthesizer:
    """Main class for the voice synthesis component"""
    
    def __init__(self, hub: CoreHub, visual_companion: VisualCompanion = None):
        self.hub = hub
        self.visual_companion = visual_companion
        self.name = "voice_synthesizer"
        self.component_type = ComponentType.VOICE
        self.active = True
        
        # Initialize voice components
        self.voice_profile = VoiceProfile(
            name="MIST",
            gender="female-presenting",
            pitch_base=0.55,  # Slightly higher for gentle, caring tone
            pitch_variance=0.1,
            speed_base=0.45,  # Slightly slower for clarity
            speed_variance=0.05,
            volume_base=0.7,
            volume_variance=0.1,
            warmth=0.85,  # High warmth for caring nature
            clarity=0.9
        )
        
        self.emotion_analyzer = EmotionAnalyzer()
        self.parameter_calculator = VoiceParameterCalculator(self.voice_profile)
        self.context_processor = ContextAwareProcessor()
        
        # State tracking
        self.current_emotional_state = EmotionalVoiceState()
        self.current_context = {}
        self.synthesis_queue = asyncio.Queue()
        
        # Register with the hub
        self.hub.registry.register_component(
            self.name,
            self.handle_message,
            self.component_type
        )
        
        # Register for relevant events
        self.hub.event_coord.register_event_handler("text_to_synthesize", self.on_text_synthesis_request)
        self.hub.event_coord.register_event_handler("context_update", self.on_context_update)
        self.hub.event_coord.register_event_handler("emotion_update", self.on_emotion_update)
    
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        if not self.active:
            return
        
        # Process different types of messages
        if message.content.get("type") == "synthesize_request":
            text = message.content.get("text", "")
            context = message.content.get("context", {})
            await self.synthesize_text(text, context, message.source)
        
        elif message.content.get("type") == "get_voice_state":
            # Return current voice state
            voice_state = self.get_current_voice_state()
            response_msg = Message(
                id=f"{message.id}_response",
                source=self.name,
                destination=message.source,
                content={
                    "type": "voice_state",
                    "state": voice_state
                },
                context={"response_to": message.id}
            )
            await self.hub.send_message(response_msg)
    
    async def synthesize_text(self, text: str, context: Dict[str, Any] = None, requester: str = None):
        """Synthesize text with appropriate emotional expression"""
        if not text.strip():
            return
        
        # Analyze emotion in the text
        emotional_state = self.emotion_analyzer.analyze_emotion(text, context or {})
        
        # Process context influences
        context_influences = self.context_processor.get_context_influences(context or {})
        
        # Calculate speech parameters
        params = self.parameter_calculator.calculate_parameters(emotional_state, text)
        
        # Apply context influences
        params.pitch = max(0.0, min(1.0, params.pitch + context_influences["time_of_day_pitch"]))
        params.speed = max(0.1, min(0.9, params.speed + (context_influences["energy_level"] - 0.5) * 0.2))
        
        # Create synthesis result
        synthesis_result = {
            "text": text,
            "parameters": params.__dict__,
            "emotional_state": emotional_state.__dict__,
            "context_influences": context_influences,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to requester if specified
        if requester:
            response_msg = Message(
                id=f"synthesis_result_{datetime.now().timestamp()}",
                source=self.name,
                destination=requester,
                content={
                    "type": "synthesis_complete",
                    "result": synthesis_result
                }
            )
            await self.hub.send_message(response_msg)
        
        # Also send emotional state to visual companion for synchronization
        if self.visual_companion:
            emotion_msg = Message(
                id=f"emotion_sync_{datetime.now().timestamp()}",
                source=self.name,
                destination="visual_companion",
                content={
                    "type": "emotion_update",
                    "emotion": emotional_state.emotion,
                    "intensity": emotional_state.intensity
                }
            )
            await self.hub.send_message(emotion_msg)
        
        # Update internal state
        self.current_emotional_state = emotional_state
        if context:
            self.current_context.update(context)
    
    def get_current_voice_state(self) -> Dict[str, Any]:
        """Get the current voice state"""
        return {
            "profile": self.voice_profile.__dict__,
            "emotional_state": self.current_emotional_state.__dict__,
            "current_context": self.current_context,
            "timestamp": datetime.now().isoformat()
        }
    
    async def on_text_synthesis_request(self, event_type: str, data: Any):
        """Handle text synthesis requests"""
        if data and isinstance(data, dict):
            text = data.get("text", "")
            context = data.get("context", {})
            requester = data.get("requester")
            
            if text:
                await self.synthesize_text(text, context, requester)
    
    async def on_context_update(self, event_type: str, data: Any):
        """Handle context updates"""
        if data and isinstance(data, dict):
            self.current_context.update(data)
    
    async def on_emotion_update(self, event_type: str, data: Any):
        """Handle emotion updates from other components"""
        if data and isinstance(data, dict):
            emotion = data.get("emotion", "neutral")
            intensity = data.get("intensity", 0.5)
            self.current_emotional_state = EmotionalVoiceState(
                emotion=emotion,
                intensity=intensity
            )
    
    async def update_loop(self):
        """Main update loop for the voice synthesizer"""
        while self.active:
            try:
                # Process synthesis requests from queue if any
                try:
                    # Non-blocking check for queued items
                    item = self.synthesis_queue.get_nowait()
                    text, context, requester = item
                    await self.synthesize_text(text, context, requester)
                except asyncio.QueueEmpty:
                    pass
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error in voice synthesizer update loop: {e}")
                await asyncio.sleep(1)  # Pause on error


# Example usage
async def main():
    # Initialize the core hub
    hub = CoreHub()
    await hub.start()
    
    # Create the visual companion first (needed for voice synch)
    visual_comp = VisualCompanion(hub)
    
    # Create the voice synthesizer
    voice_synthesizer = VoiceSynthesizer(hub, visual_comp)
    
    # Start the update loops in background
    voice_update_task = asyncio.create_task(voice_synthesizer.update_loop())
    
    # Simulate some interactions
    await asyncio.sleep(1)
    
    # Send a text synthesis request
    synthesis_msg = Message(
        id="test_synthesis_1",
        source="conversation_engine",
        destination="voice_synthesizer",
        content={
            "type": "synthesize_request",
            "text": "Hello there! I'm so glad we're connecting today. It feels wonderful to be here with you.",
            "context": {
                "time_of_day": "afternoon",
                "user_attention": 0.8
            }
        }
    )
    await hub.send_message(synthesis_msg)
    
    await asyncio.sleep(2)
    
    # Send another synthesis request with different emotion
    synthesis_msg2 = Message(
        id="test_synthesis_2",
        source="conversation_engine",
        destination="voice_synthesizer",
        content={
            "type": "synthesize_request",
            "text": "I've been thinking about Mars and the amazing possibilities that await us there. It's truly fascinating!",
            "context": {
                "time_of_day": "afternoon",
                "topic": "Mars exploration",
                "user_attention": 0.9
            }
        }
    )
    await hub.send_message(synthesis_msg2)
    
    await asyncio.sleep(2)
    
    # Request current voice state
    state_msg = Message(
        id="request_state_1",
        source="debugger",
        destination="voice_synthesizer",
        content={
            "type": "get_voice_state"
        }
    )
    await hub.send_message(state_msg)
    
    # Let it run for a bit
    await asyncio.sleep(5)
    
    # Cancel tasks and shut down
    voice_update_task.cancel()
    await hub.shutdown()


if __name__ == "__main__":
    # Uncomment to run the example
    # asyncio.run(main())
    pass