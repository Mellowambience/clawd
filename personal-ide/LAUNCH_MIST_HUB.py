#!/usr/bin/env python3
"""
Launch Script for MIST Companion Intelligence Hub
Starts all components and connects them through the CoreHub
"""

import asyncio
import signal
import sys
from typing import List

from integration.CORE_HUB import CoreHub
from integration.AI_CONNECTOR import AIConnector
from memory.MEMORY_NODES import MemoryWeb
from visualization.VISUAL_COMPANION import VisualCompanion
from voice.VOICE_SYNTHESIZER import VoiceSynthesizer
from x_integration.X_INTEGRATION import XIntegration


class MISTHub:
    """Main orchestrator for the MIST Companion Intelligence system"""
    
    def __init__(self):
        self.hub = CoreHub()
        self.visual_companion = None
        self.voice_synthesizer = None
        self.memory_web = None
        self.ai_connector = None
        
        # Tasks for component loops
        self.tasks: List[asyncio.Task] = []
        self.running = True
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def initialize_components(self):
        """Initialize all system components"""
        print("Initializing MIST Companion Intelligence Hub...")
        
        # Start the core hub
        await self.hub.start()
        print("✓ Core Hub initialized")
        
        # Initialize components in dependency order
        self.visual_companion = VisualCompanion(self.hub)
        print("✓ Visual Companion initialized")
        
        self.voice_synthesizer = VoiceSynthesizer(self.hub, self.visual_companion)
        print("✓ Voice Synthesizer initialized")
        
        self.memory_web = MemoryWeb(self.hub, self.visual_companion, self.voice_synthesizer)
        print("✓ Memory Web initialized")
        
        self.ai_connector = AIConnector(self.hub, self.memory_web, self.visual_companion, self.voice_synthesizer)
        print("✓ AI Connector initialized")
        
        self.x_integration = XIntegration(self.hub)
        print("✓ X Integration initialized")
        
        # Connect components
        self.hub.connect_components("ai_connector", "memory_web")
        self.hub.connect_components("memory_web", "voice_synthesizer")
        self.hub.connect_components("voice_synthesizer", "visual_companion")
        self.hub.connect_components("visual_companion", "ai_connector")
        self.hub.connect_components("ai_connector", "x_integration")
        self.hub.connect_components("memory_web", "x_integration")
        
        print("✓ Components connected")
    
    async def start_component_loops(self):
        """Start update loops for all components"""
        print("Starting component update loops...")
        
        # Create tasks for each component's update loop
        self.tasks.append(asyncio.create_task(self.visual_companion.update_loop()))
        self.tasks.append(asyncio.create_task(self.voice_synthesizer.update_loop()))
        self.tasks.append(asyncio.create_task(self.memory_web.update_loop()))
        self.tasks.append(asyncio.create_task(self.ai_connector.update_loop()))
        # Note: X integration doesn't have a continuous update loop like other components
        
        print("✓ All component loops started")
        
        # Send a startup notification
        startup_msg = {
            "type": "system_notification",
            "event": "hub_startup",
            "timestamp": asyncio.get_event_loop().time(),
            "components": {
                "visual_companion": "active",
                "voice_synthesizer": "active", 
                "memory_web": "active",
                "ai_connector": "active"
            }
        }
        
        await self.hub.trigger_event("system_notification", startup_msg)
    
    async def run(self):
        """Run the MIST Hub"""
        try:
            await self.initialize_components()
            await self.start_component_loops()
            
            print("\n=== MIST Companion Intelligence Hub is now running ===")
            print("Features available:")
            print("- Visual companion with emotional expressions")
            print("- Multi-model AI with smart routing")
            print("- Distributed memory system")
            print("- Voice synthesis with emotional awareness")
            print("- Local social hub (visit http://localhost:8082)")
            print("- X platform integration (when configured)")
            print("\nPress Ctrl+C to shutdown gracefully")
            
            # Keep running until shutdown signal
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"Error running MIST Hub: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Gracefully shut down all components"""
        print("\nShutting down MIST Hub...")
        
        # Cancel all running tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to finish with timeout
        if self.tasks:
            await asyncio.wait(self.tasks, timeout=5.0)
        
        # Shut down the core hub
        await self.hub.shutdown()
        
        print("MIST Hub shutdown complete")


async def main():
    """Main entry point"""
    hub = MISTHub()
    await hub.run()


if __name__ == "__main__":
    # Run the MIST Hub
    asyncio.run(main())