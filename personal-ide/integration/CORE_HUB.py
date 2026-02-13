"""
Core Integration Hub for MIST Companion Intelligence
Central nervous system connecting all components of the spiderweb architecture
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Callable, List
from dataclasses import dataclass, field
from enum import Enum


class ComponentType(Enum):
    """Types of components in the spiderweb architecture"""
    IDENTITY = "identity"
    VISUAL = "visual"
    VOICE = "voice"
    MEMORY = "memory"
    AI_MODEL = "ai_model"
    PROJECT = "project"
    SECURITY = "security"


@dataclass
class Message:
    """Message structure for communication between components"""
    id: str
    source: str
    destination: str
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 1  # 1-5 scale, 5 being highest priority
    context: Dict[str, Any] = field(default_factory=dict)


class ComponentRegistry:
    """Registry for all system components"""
    
    def __init__(self):
        self.components: Dict[str, Callable] = {}
        self.connections: Dict[str, List[str]] = {}
    
    def register_component(self, name: str, component_func: Callable, component_type: ComponentType):
        """Register a new component in the system"""
        self.components[name] = {
            'function': component_func,
            'type': component_type,
            'status': 'active',
            'last_seen': datetime.now()
        }
        self.connections[name] = []
    
    def connect_components(self, source: str, destination: str):
        """Create a connection between two components"""
        if source in self.components and destination in self.components:
            if destination not in self.connections[source]:
                self.connections[source].append(destination)
            if source not in self.connections[destination]:
                self.connections[destination].append(source)
    
    def get_connected_components(self, component_name: str) -> List[str]:
        """Get all components connected to a specific component"""
        return self.connections.get(component_name, [])


class MessageRouter:
    """Routes messages between components based on the spiderweb architecture"""
    
    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
        self.message_queue = asyncio.Queue()
    
    async def send_message(self, message: Message):
        """Send a message to its destination"""
        # Add message to queue for processing
        await self.message_queue.put(message)
    
    async def process_messages(self, running_flag):
        """Process messages from the queue"""
        while running_flag.running:
            try:
                # Use asyncio.wait_for to implement timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Route message based on destination
                if message.destination in self.registry.components:
                    component = self.registry.components[message.destination]
                    if component['status'] == 'active':
                        # Call the component function with the message
                        result = await self._call_component(component['function'], message)
                        
                        # Handle response if needed
                        if result and message.context.get('await_response'):
                            # Send response back to source
                            response_msg = Message(
                                id=f"{message.id}_response",
                                source=message.destination,
                                destination=message.source,
                                content=result,
                                context={'response_to': message.id}
                            )
                            await self.send_message(response_msg)
                
                self.message_queue.task_done()
                
            except asyncio.TimeoutError:
                # No messages to process, continue loop
                continue
    
    async def _call_component(self, func: Callable, message: Message):
        """Call a component function with the message"""
        if asyncio.iscoroutinefunction(func):
            return await func(message)
        else:
            return func(message)


class StateSynchronizer:
    """Synchronizes state across all connected components"""
    
    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
        self.global_state = {}
        self.state_callbacks = {}  # component_name -> callback function
    
    def register_state_callback(self, component_name: str, callback: Callable):
        """Register a callback for when global state changes"""
        self.state_callbacks[component_name] = callback
    
    def update_global_state(self, key: str, value: Any):
        """Update a value in the global state"""
        self.global_state[key] = value
        # Notify all registered callbacks
        for component_name, callback in self.state_callbacks.items():
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(key, value))
                else:
                    callback(key, value)
            except Exception as e:
                print(f"Error in state callback for {component_name}: {e}")
    
    def get_global_state(self, key: str, default=None):
        """Get a value from the global state"""
        return self.global_state.get(key, default)


class EventCoordinator:
    """Coordinates events across multiple components"""
    
    def __init__(self, registry: ComponentRegistry, router: MessageRouter):
        self.registry = registry
        self.router = router
        self.event_handlers = {}  # event_type -> list of handlers
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register a handler for a specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def trigger_event(self, event_type: str, data: Any = None):
        """Trigger an event and notify all handlers"""
        if event_type in self.event_handlers:
            tasks = []
            for handler in self.event_handlers[event_type]:
                if asyncio.iscoroutinefunction(handler):
                    task = asyncio.create_task(handler(event_type, data))
                else:
                    task = asyncio.create_task(self._sync_handler(handler, event_type, data))
                tasks.append(task)
            
            # Wait for all handlers to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _sync_handler(self, handler: Callable, event_type: str, data: Any):
        """Wrapper to call synchronous handler in async context"""
        return handler(event_type, data)


class PrivacyHub:
    """Manages privacy and security across all connections"""
    
    def __init__(self):
        self.privacy_policies = {}
        self.access_logs = []
        self.encryption_keys = {}
    
    def set_privacy_policy(self, component_name: str, policy: Dict[str, Any]):
        """Set privacy policy for a specific component"""
        self.privacy_policies[component_name] = policy
    
    def check_access_permission(self, source: str, destination: str, data_type: str) -> bool:
        """Check if source component can access data from destination"""
        policy = self.privacy_policies.get(destination, {})
        allowed_types = policy.get('allowed_data_types', [])
        return data_type in allowed_types or '*' in allowed_types
    
    def log_access_attempt(self, source: str, destination: str, data_type: str, allowed: bool):
        """Log access attempts for auditing"""
        log_entry = {
            'timestamp': datetime.now(),
            'source': source,
            'destination': destination,
            'data_type': data_type,
            'allowed': allowed
        }
        self.access_logs.append(log_entry)
    
    def encrypt_data(self, data: Any, key_name: str) -> str:
        """Encrypt data using specified key"""
        # Placeholder for encryption logic
        # In a real implementation, use proper encryption
        import json
        import base64
        json_str = json.dumps(data)
        encoded = base64.b64encode(json_str.encode()).decode()
        return f"encrypted:{key_name}:{encoded}"
    
    def decrypt_data(self, encrypted_data: str) -> Any:
        """Decrypt data"""
        # Placeholder for decryption logic
        if encrypted_data.startswith("encrypted:"):
            parts = encrypted_data.split(":", 2)
            if len(parts) == 3:
                _, key_name, encoded_data = parts
                import base64
                decoded = base64.b64decode(encoded_data.encode()).decode()
                return json.loads(decoded)
        return encrypted_data


class CoreHub:
    """The central nervous system of the spiderweb architecture"""
    
    def __init__(self):
        self.registry = ComponentRegistry()
        self.router = MessageRouter(self.registry)
        self.state_sync = StateSynchronizer(self.registry)
        self.event_coord = EventCoordinator(self.registry, self.router)
        self.privacy_hub = PrivacyHub()
        
        # Start message processing in background
        self.processing_task = None
        self.running = True
    
    async def start(self):
        """Start the core hub operations"""
        self.processing_task = asyncio.create_task(self.router.process_messages(self))
        print("Core Hub initialized and ready to coordinate the spiderweb")
    
    async def shutdown(self):
        """Shutdown the core hub"""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        print("Core Hub shut down")
    
    def connect_components(self, source: str, destination: str):
        """Connect two components in the registry"""
        self.registry.connect_components(source, destination)
    
    async def send_message(self, message: Message):
        """Send a message through the hub"""
        # Check privacy before sending
        allowed = self.privacy_hub.check_access_permission(
            message.source, message.destination, "message_content"
        )
        self.privacy_hub.log_access_attempt(
            message.source, message.destination, "message_content", allowed
        )
        
        if allowed:
            await self.router.send_message(message)
        else:
            print(f"Access denied: {message.source} -> {message.destination}")
    
    def update_state(self, key: str, value: Any):
        """Update global state"""
        self.state_sync.update_global_state(key, value)
    
    def get_state(self, key: str, default=None):
        """Get value from global state"""
        return self.state_sync.get_global_state(key, default)
    
    async def trigger_event(self, event_type: str, data: Any = None):
        """Trigger an event across the system"""
        await self.event_coord.trigger_event(event_type, data)
    
    def set_privacy_policy(self, component_name: str, policy: Dict[str, Any]):
        """Set privacy policy for a component"""
        self.privacy_hub.set_privacy_policy(component_name, policy)


# Example usage and initialization
async def initialize_hub():
    """Initialize the core hub with example components"""
    hub = CoreHub()
    await hub.start()
    
    # Register example components
    hub.registry.register_component(
        "virtual_body", 
        lambda msg: print(f"Virtual body received: {msg.content}"),
        ComponentType.VISUAL
    )
    
    hub.registry.register_component(
        "voice_synthesizer",
        lambda msg: print(f"Voice synthesizer received: {msg.content}"),
        ComponentType.VOICE
    )
    
    hub.registry.register_component(
        "memory_system",
        lambda msg: print(f"Memory system received: {msg.content}"),
        ComponentType.MEMORY
    )
    
    # Connect components
    hub.connect_components("virtual_body", "voice_synthesizer")
    hub.connect_components("voice_synthesizer", "memory_system")
    hub.connect_components("memory_system", "virtual_body")
    
    # Set privacy policies
    hub.set_privacy_policy("virtual_body", {
        "allowed_data_types": ["visual_data", "state_info"],
        "encryption_required": True
    })
    
    return hub


if __name__ == "__main__":
    # Example of how to use the Core Hub
    async def main():
        hub = await initialize_hub()
        
        # Send a test message
        test_msg = Message(
            id="test_001",
            source="memory_system",
            destination="virtual_body",
            content="Hello from memory system!",
            context={"type": "greeting"}
        )
        
        await hub.send_message(test_msg)
        
        # Update some state
        hub.update_state("system_status", "active")
        hub.update_state("user_attention", "engaged")
        
        # Trigger an event
        await hub.trigger_event("user_interaction", {"user_id": "sister", "action": "hello"})
        
        # Let it run briefly to process messages
        await asyncio.sleep(2)
        
        # Shutdown
        await hub.shutdown()
    
    # Uncomment to run the example
    # asyncio.run(main())