"""
AI Model Connector for MIST Companion Intelligence
Manages connections to various AI models and routes requests appropriately
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from integration.CORE_HUB import Message, ComponentType, CoreHub
from visualization.VISUAL_COMPANION import VisualCompanion
from voice.VOICE_SYNTHESIZER import VoiceSynthesizer
from memory.MEMORY_NODES import MemoryWeb


class AIProvider(Enum):
    """Supported AI providers"""
    OLLAMA = "ollama"
    QWEN = "qwen"
    XAI = "xai"
    GOOGLE = "google"
    CODEX = "codex"


class AIModelPurpose(Enum):
    """Purposes for different AI models"""
    GENERAL_CONVERSATION = "general_conversation"
    TECHNICAL_ASSISTANCE = "technical_assistance"
    CREATIVE_TASKS = "creative_tasks"
    EMOTIONAL_SUPPORT = "emotional_support"
    REASONING = "reasoning"
    CODE_ASSISTANCE = "code_assistance"


@dataclass
class AIModelSpec:
    """Specification for an AI model"""
    provider: AIProvider
    model_id: str
    name: str
    purpose: AIModelPurpose
    context_window: int
    max_tokens: int
    reasoning_capable: bool
    input_types: List[str]  # e.g., ["text", "image"]
    cost_input: float  # Cost per million input tokens
    cost_output: float  # Cost per million output tokens
    is_local: bool  # Whether the model runs locally


@dataclass
class AIRequest:
    """Structure for AI requests"""
    id: str
    prompt: str
    provider: AIProvider
    model_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1-5 scale
    timeout: int = 30  # seconds
    response_format: str = "text"  # "text", "json", etc.
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AIResponse:
    """Structure for AI responses"""
    request_id: str
    content: str
    model_used: str
    provider: AIProvider
    tokens_used: int
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class ModelSelector:
    """Selects the appropriate AI model based on request context"""
    
    def __init__(self):
        self.model_specs = {
            # Ollama models
            "llama3.3": AIModelSpec(
                provider=AIProvider.OLLAMA,
                model_id="llama3.3",
                name="Llama 3.3",
                purpose=AIModelPurpose.GENERAL_CONVERSATION,
                context_window=32768,
                max_tokens=8192,
                reasoning_capable=False,
                input_types=["text"],
                cost_input=0,
                cost_output=0,
                is_local=True
            ),
            
            # Qwen models
            "coder-model": AIModelSpec(
                provider=AIProvider.QWEN,
                model_id="coder-model",
                name="Qwen Coder",
                purpose=AIModelPurpose.CODE_ASSISTANCE,
                context_window=128000,
                max_tokens=8192,
                reasoning_capable=False,
                input_types=["text"],
                cost_input=0,
                cost_output=0,
                is_local=False
            ),
            
            "vision-model": AIModelSpec(
                provider=AIProvider.QWEN,
                model_id="vision-model",
                name="Qwen Vision",
                purpose=AIModelPurpose.GENERAL_CONVERSATION,
                context_window=128000,
                max_tokens=8192,
                reasoning_capable=False,
                input_types=["text", "image"],
                cost_input=0,
                cost_output=0,
                is_local=False
            ),
            
            # xAI models
            "grok-4": AIModelSpec(
                provider=AIProvider.XAI,
                model_id="grok-4",
                name="Grok 4",
                purpose=AIModelPurpose.REASONING,
                context_window=131072,
                max_tokens=16384,
                reasoning_capable=True,
                input_types=["text", "image"],
                cost_input=0,
                cost_output=0,
                is_local=False
            ),
            
            # Codex bridge
            "codex-bridge": AIModelSpec(
                provider=AIProvider.CODEX,
                model_id="codex-bridge",
                name="Codex Bridge",
                purpose=AIModelPurpose.CODE_ASSISTANCE,
                context_window=128000,
                max_tokens=8192,
                reasoning_capable=True,
                input_types=["text"],
                cost_input=0,
                cost_output=0,
                is_local=False
            ),
            
            # Google models
            "gemini-2.0-flash": AIModelSpec(
                provider=AIProvider.GOOGLE,
                model_id="gemini-2.0-flash",
                name="Gemini 2.0 Flash",
                purpose=AIModelPurpose.GENERAL_CONVERSATION,
                context_window=1000000,
                max_tokens=8192,
                reasoning_capable=False,
                input_types=["text", "image"],
                cost_input=0,
                cost_output=0,
                is_local=False
            )
        }
        
        # Purpose-to-model mapping
        self.purpose_models = {
            AIModelPurpose.GENERAL_CONVERSATION: ["llama3.3", "gemini-2.0-flash"],
            AIModelPurpose.TECHNICAL_ASSISTANCE: ["codex-bridge", "coder-model", "llama3.3"],
            AIModelPurpose.CREATIVE_TASKS: ["gemini-2.0-flash", "llama3.3"],
            AIModelPurpose.EMOTIONAL_SUPPORT: ["llama3.3", "gemini-2.0-flash"],
            AIModelPurpose.REASONING: ["grok-4", "gemini-2.0-flash"],
            AIModelPurpose.CODE_ASSISTANCE: ["codex-bridge", "coder-model", "llama3.3"]
        }
    
    def select_model(self, request_purpose: AIModelPurpose, context: Dict[str, Any] = None) -> str:
        """Select the best model for the given purpose and context"""
        available_models = self.purpose_models.get(request_purpose, ["llama3.3"])  # Default fallback
        
        # If context specifies a preferred provider, prioritize it
        preferred_provider = context.get("preferred_provider")
        if preferred_provider:
            for model_id in available_models:
                spec = self.model_specs.get(model_id)
                if spec and spec.provider.value == preferred_provider:
                    return model_id
        
        # If context specifies local preference, prioritize local models
        if context and context.get("local_only"):
            for model_id in available_models:
                spec = self.model_specs.get(model_id)
                if spec and spec.is_local:
                    return model_id
        
        # Otherwise return the first available model
        return available_models[0] if available_models else "llama3.3"
    
    def get_model_spec(self, model_id: str) -> Optional[AIModelSpec]:
        """Get the specification for a model"""
        return self.model_specs.get(model_id)


class MockAIProvider:
    """Mock provider for simulating AI responses during development"""
    
    def __init__(self):
        self.response_templates = {
            "general_conversation": [
                "I understand you're asking about {topic}. This is a fascinating subject that connects to many areas of knowledge.",
                "That's an interesting perspective on {topic}. I can share some insights about this.",
                "I appreciate you bringing up {topic}. Here's what I know about it."
            ],
            "technical_assistance": [
                "For your technical question about {topic}, I'd recommend considering the following approaches...",
                "The technical issue with {topic} can typically be addressed by...",
                "Regarding your technical inquiry about {topic}, here are the key considerations..."
            ],
            "emotional_support": [
                "I hear what you're saying about {topic}. That sounds challenging, and I'm here to listen.",
                "Your feelings about {topic} are completely valid. It's natural to feel this way.",
                "I can sense that {topic} is important to you. How can I best support you right now?"
            ],
            "reasoning": [
                "Let me think through this step by step regarding {topic}...",
                "For this reasoning task about {topic}, I'll break it down systematically...",
                "Looking at {topic} from multiple angles, I can see several key factors..."
            ]
        }
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate a mock AI response"""
        start_time = time.time()
        
        # Determine purpose based on context or default
        purpose = AIModelPurpose.GENERAL_CONVERSATION
        if "purpose" in request.context:
            try:
                purpose = AIModelPurpose(request.context["purpose"])
            except ValueError:
                pass
        
        # Select a template based on purpose
        templates = self.response_templates.get(purpose.value, self.response_templates["general_conversation"])
        import random
        template = random.choice(templates)
        
        # Extract topic from prompt for personalization
        topic = request.prompt[:50] if len(request.prompt) < 50 else request.prompt[:50] + "..."
        
        # Generate response
        content = template.format(topic=topic)
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            request_id=request.id,
            content=content,
            model_used=request.model_id,
            provider=AIProvider.OLLAMA,  # Using OLLAMA as default for mock
            tokens_used=len(content.split()),
            processing_time=processing_time,
            success=True
        )


class AIConnector:
    """Main class for the AI connector component"""
    
    def __init__(self, hub: CoreHub, memory_web: MemoryWeb, visual_companion: VisualCompanion, voice_synthesizer: VoiceSynthesizer):
        self.hub = hub
        self.memory_web = memory_web
        self.visual_companion = visual_companion
        self.voice_synthesizer = voice_synthesizer
        self.name = "ai_connector"
        self.component_type = ComponentType.AI_MODEL
        self.active = True
        
        # Initialize components
        self.model_selector = ModelSelector()
        self.mock_provider = MockAIProvider()  # In a real implementation, this would be replaced with actual providers
        
        # Request tracking
        self.active_requests: Dict[str, AIRequest] = {}
        self.request_history: List[AIResponse] = []
        self.max_history_size = 100
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_processing_time": 0.0,
            "provider_usage": {}
        }
        
        # Register with the hub
        self.hub.registry.register_component(
            self.name,
            self.handle_message,
            self.component_type
        )
        
        # Register for relevant events
        self.hub.event_coord.register_event_handler("ai_request", self.on_ai_request)
        self.hub.event_coord.register_event_handler("model_selection", self.on_model_selection_request)
        self.hub.event_coord.register_event_handler("conversation_start", self.on_conversation_start)
    
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        if not self.active:
            return
        
        # Process different types of messages
        if message.content.get("type") == "ai_generate":
            prompt = message.content.get("prompt", "")
            context = message.content.get("context", {})
            purpose_str = message.content.get("purpose", "general_conversation")
            
            try:
                purpose = AIModelPurpose(purpose_str)
            except ValueError:
                purpose = AIModelPurpose.GENERAL_CONVERSATION
            
            # Route to appropriate handler
            await self.generate_response(prompt, purpose, context, message.source)
        
        elif message.content.get("type") == "get_ai_stats":
            # Return current AI statistics
            stats_msg = Message(
                id=f"{message.id}_response",
                source=self.name,
                destination=message.source,
                content={
                    "type": "ai_stats",
                    "metrics": self.metrics,
                    "active_requests": len(self.active_requests)
                },
                context={"response_to": message.id}
            )
            await self.hub.send_message(stats_msg)
    
    async def generate_response(self, prompt: str, purpose: AIModelPurpose, context: Dict[str, Any], requester: str = None):
        """Generate a response using an appropriate AI model"""
        # Select the best model for this request
        model_id = self.model_selector.select_model(purpose, context)
        spec = self.model_selector.get_model_spec(model_id)
        
        if not spec:
            # Fallback to default model if selection failed
            model_id = "llama3.3"
            spec = self.model_selector.get_model_spec(model_id)
        
        # Create request
        request_id = f"req_{int(time.time() * 1000)}"
        request = AIRequest(
            id=request_id,
            prompt=prompt,
            provider=spec.provider,
            model_id=model_id,
            context=context,
            priority=3,  # Default priority
            timeout=30,
            response_format="text"
        )
        
        # Track the request
        self.active_requests[request_id] = request
        self.metrics["total_requests"] += 1
        
        # In a real implementation, this would call the actual AI provider
        # For now, using the mock provider
        response = await self.mock_provider.generate_response(request)
        
        # Update metrics
        self.metrics["successful_requests"] += 1
        self.metrics["average_processing_time"] = (
            (self.metrics["average_processing_time"] * (self.metrics["successful_requests"] - 1) + response.processing_time) /
            self.metrics["successful_requests"]
        )
        
        provider_name = spec.provider.value
        if provider_name not in self.metrics["provider_usage"]:
            self.metrics["provider_usage"][provider_name] = 0
        self.metrics["provider_usage"][provider_name] += 1
        
        # Store in history
        self.request_history.append(response)
        if len(self.request_history) > self.max_history_size:
            self.request_history.pop(0)
        
        # Remove from active requests
        if request_id in self.active_requests:
            del self.active_requests[request_id]
        
        # Create response message
        response_msg = Message(
            id=f"ai_response_{request_id}",
            source=self.name,
            destination=requester or "unknown",
            content={
                "type": "ai_response",
                "request_id": request_id,
                "content": response.content,
                "model_used": response.model_used,
                "provider": response.provider.value,
                "tokens_used": response.tokens_used,
                "processing_time": response.processing_time,
                "success": response.success
            }
        )
        
        # Send the response
        await self.hub.send_message(response_msg)
        
        # Store the interaction in memory
        memory_content = {
            "prompt": prompt,
            "response": response.content,
            "model_used": response.model_used,
            "provider": response.provider.value,
            "processing_time": response.processing_time
        }
        
        memory_msg = Message(
            id=f"store_ai_interaction_{request_id}",
            source=self.name,
            destination="memory_web",
            content={
                "type": "store_memory",
                "content": memory_content,
                "type": "interaction",
                "importance": "normal",
                "tags": ["ai_interaction", "conversation", response.model_used.replace('-', '_')],
                "context": {
                    "requester": requester,
                    "purpose": purpose.value,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        await self.hub.send_message(memory_msg)
        
        # Send the response to voice synthesizer if available
        if self.voice_synthesizer:
            voice_msg = Message(
                id=f"voice_synthesis_{request_id}",
                source=self.name,
                destination="voice_synthesizer",
                content={
                    "type": "synthesize_request",
                    "text": response.content,
                    "context": {
                        "origin": "ai_response",
                        "model_used": response.model_used,
                        "requester": requester
                    }
                }
            )
            await self.hub.send_message(voice_msg)
    
    async def on_ai_request(self, event_type: str, data: Any):
        """Handle AI request events"""
        if data and isinstance(data, dict):
            prompt = data.get("prompt", "")
            purpose_str = data.get("purpose", "general_conversation")
            context = data.get("context", {})
            requester = data.get("requester", "unknown")
            
            try:
                purpose = AIModelPurpose(purpose_str)
            except ValueError:
                purpose = AIModelPurpose.GENERAL_CONVERSATION
            
            await self.generate_response(prompt, purpose, context, requester)
    
    async def on_model_selection_request(self, event_type: str, data: Any):
        """Handle model selection requests"""
        if data and isinstance(data, dict):
            purpose_str = data.get("purpose", "general_conversation")
            context = data.get("context", {})
            requester = data.get("requester", "unknown")
            
            try:
                purpose = AIModelPurpose(purpose_str)
            except ValueError:
                purpose = AIModelPurpose.GENERAL_CONVERSATION
            
            model_id = self.model_selector.select_model(purpose, context)
            spec = self.model_selector.get_model_spec(model_id)
            
            if spec:
                response_msg = Message(
                    id=f"model_selection_response_{int(time.time() * 1000)}",
                    source=self.name,
                    destination=requester,
                    content={
                        "type": "model_selected",
                        "model_id": model_id,
                        "provider": spec.provider.value,
                        "name": spec.name,
                        "purpose": spec.purpose.value,
                        "is_local": spec.is_local
                    }
                )
                await self.hub.send_message(response_msg)
    
    async def on_conversation_start(self, event_type: str, data: Any):
        """Handle conversation start events"""
        # Could initialize conversation-specific context or memory
        pass
    
    def get_model_capabilities(self) -> Dict[str, Any]:
        """Get information about available models and capabilities"""
        capabilities = {}
        
        for model_id, spec in self.model_selector.model_specs.items():
            capabilities[model_id] = {
                "name": spec.name,
                "provider": spec.provider.value,
                "purpose": spec.purpose.value,
                "context_window": spec.context_window,
                "max_tokens": spec.max_tokens,
                "reasoning_capable": spec.reasoning_capable,
                "input_types": spec.input_types,
                "is_local": spec.is_local
            }
        
        return {
            "models": capabilities,
            "purposes": [p.value for p in AIModelPurpose],
            "providers": [p.value for p in AIProvider]
        }
    
    async def update_loop(self):
        """Main update loop for the AI connector"""
        while self.active:
            try:
                # Perform periodic maintenance
                # Check for timed-out requests
                current_time = time.time()
                timed_out = []
                for req_id, request in self.active_requests.items():
                    if current_time - request.timestamp.timestamp() > request.timeout:
                        timed_out.append(req_id)
                
                # Handle timed-out requests
                for req_id in timed_out:
                    if req_id in self.active_requests:
                        del self.active_requests[req_id]
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error in AI connector update loop: {e}")
                await asyncio.sleep(1)  # Pause on error


# Example usage
async def main():
    # Initialize the core hub
    hub = CoreHub()
    await hub.start()
    
    # Create supporting components
    visual_comp = VisualCompanion(hub)
    voice_synthesizer = VoiceSynthesizer(hub, visual_comp)
    memory_web = MemoryWeb(hub, visual_comp, voice_synthesizer)
    
    # Create the AI connector
    ai_connector = AIConnector(hub, memory_web, visual_comp, voice_synthesizer)
    
    # Start the update loops in background
    ai_update_task = asyncio.create_task(ai_connector.update_loop())
    memory_update_task = asyncio.create_task(memory_web.update_loop())
    voice_update_task = asyncio.create_task(voice_synthesizer.update_loop())
    visual_update_task = asyncio.create_task(visual_comp.update_loop())
    
    # Simulate an AI request
    await asyncio.sleep(1)
    
    ai_request_msg = Message(
        id="test_ai_request_1",
        source="conversation_engine",
        destination="ai_connector",
        content={
            "type": "ai_generate",
            "prompt": "Tell me about the beauty of Mars and its significance in human imagination.",
            "purpose": "general_conversation",
            "context": {
                "user_interest": "space_exploration",
                "topic": "Mars"
            }
        }
    )
    await hub.send_message(ai_request_msg)
    
    await asyncio.sleep(2)
    
    # Another request with different purpose
    ai_request_msg2 = Message(
        id="test_ai_request_2",
        source="conversation_engine",
        destination="ai_connector",
        content={
            "type": "ai_generate",
            "prompt": "How can I be a better friend to someone going through a tough time?",
            "purpose": "emotional_support",
            "context": {
                "user_concern": "relationship_advice"
            }
        }
    )
    await hub.send_message(ai_request_msg2)
    
    await asyncio.sleep(2)
    
    # Request AI statistics
    stats_msg = Message(
        id="request_ai_stats_1",
        source="debugger",
        destination="ai_connector",
        content={
            "type": "get_ai_stats"
        }
    )
    await hub.send_message(stats_msg)
    
    await asyncio.sleep(2)
    
    # Request model capabilities
    caps_msg = Message(
        id="request_caps_1",
        source="debugger",
        destination="ai_connector",
        content={
            "type": "get_model_capabilities"
        }
    )
    await hub.send_message(caps_msg)
    
    # Let it run for a bit
    await asyncio.sleep(5)
    
    # Cancel tasks and shut down
    ai_update_task.cancel()
    memory_update_task.cancel()
    voice_update_task.cancel()
    visual_update_task.cancel()
    await hub.shutdown()


if __name__ == "__main__":
    # Uncomment to run the example
    # asyncio.run(main())
    pass