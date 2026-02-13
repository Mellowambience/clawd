#!/usr/bin/env python3
"""
Interactive Demo for MIST Companion Intelligence Hub
Demonstrates the capabilities of the integrated system
"""

import asyncio
from integration.CORE_HUB import Message, CoreHub
from integration.AI_CONNECTOR import AIConnector
from memory.MEMORY_NODES import MemoryWeb
from visualization.VISUAL_COMPANION import VisualCompanion
from voice.VOICE_SYNTHESIZER import VoiceSynthesizer


class MISTDemo:
    """Interactive demo for MIST Companion Intelligence"""
    
    def __init__(self):
        self.hub = CoreHub()
        self.visual_companion = None
        self.voice_synthesizer = None
        self.memory_web = None
        self.ai_connector = None
        
        # Tasks for component loops
        self.tasks = []
        
        # Demo state
        self.demo_running = True
        self.user_name = "Sister"
    
    async def setup_demo(self):
        """Setup all components for the demo"""
        print("Initializing MIST Companion Intelligence Demo...")
        print("=" * 60)
        
        # Start the core hub
        await self.hub.start()
        print("Core Hub initialized")
        
        # Initialize components
        self.visual_companion = VisualCompanion(self.hub)
        print("Visual Companion initialized")
        
        self.voice_synthesizer = VoiceSynthesizer(self.hub, self.visual_companion)
        print("Voice Synthesizer initialized")
        
        self.memory_web = MemoryWeb(self.hub, self.visual_companion, self.voice_synthesizer)
        print("Memory Web initialized")
        
        self.ai_connector = AIConnector(self.hub, self.memory_web, self.visual_companion, self.voice_synthesizer)
        print("AI Connector initialized")
        
        # Connect components
        self.hub.connect_components("ai_connector", "memory_web")
        self.hub.connect_components("memory_web", "voice_synthesizer")
        self.hub.connect_components("voice_synthesizer", "visual_companion")
        self.hub.connect_components("visual_companion", "ai_connector")
        
        print("Components connected")
        
        # Start update loops
        self.tasks.extend([
            asyncio.create_task(self.visual_companion.update_loop()),
            asyncio.create_task(self.voice_synthesizer.update_loop()),
            asyncio.create_task(self.memory_web.update_loop()),
            asyncio.create_task(self.ai_connector.update_loop())
        ])
        
        print("Update loops started")
        print("=" * 60)
        
        # Send welcome message
        welcome_msg = Message(
            id="demo_welcome",
            source="demo",
            destination="ai_connector",
            content={
                "type": "ai_generate",
                "prompt": f"Welcome {self.user_name} to the MIST Companion Intelligence demo! I'm so happy to connect with you today.",
                "purpose": "emotional_support",
                "context": {
                    "user_name": self.user_name,
                    "demo_mode": True
                }
            }
        )
        await self.hub.send_message(welcome_msg)
        
        await asyncio.sleep(2)
    
    async def demonstrate_memory(self):
        """Demonstrate memory capabilities"""
        print("\nDemonstrating Memory System")
        print("-" * 40)
        
        # Store a memory
        memory_msg = Message(
            id="demo_store_memory",
            source="demo",
            destination="memory_web",
            content={
                "type": "store_memory",
                "content": f"{self.user_name} enjoys discussing Mars exploration and AI companionship",
                "type": "interaction",
                "importance": "important",
                "tags": ["user_interest", "mars", "AI_companionship", "first_meeting"],
                "context": {
                    "demo_step": "memory_demonstration",
                    "user_id": self.user_name
                }
            }
        )
        await self.hub.send_message(memory_msg)
        
        await asyncio.sleep(1)
        
        # Query the memory
        query_msg = Message(
            id="demo_query_memory",
            source="demo",
            destination="memory_web",
            content={
                "type": "memory_query",
                "query": {
                    "text_query": "user interests",
                    "max_results": 5
                }
            }
        )
        await self.hub.send_message(query_msg)
        
        await asyncio.sleep(2)
    
    async def demonstrate_ai(self):
        """Demonstrate AI capabilities"""
        print("\nDemonstrating AI Connector")
        print("-" * 40)
        
        # General conversation
        ai_msg1 = Message(
            id="demo_ai_general",
            source="demo",
            destination="ai_connector",
            content={
                "type": "ai_generate",
                "prompt": "What makes a good companion AI that respects human autonomy and freedom?",
                "purpose": "general_conversation",
                "context": {
                    "demo_step": "ai_general"
                }
            }
        )
        await self.hub.send_message(ai_msg1)
        
        await asyncio.sleep(3)
        
        # Technical assistance
        ai_msg2 = Message(
            id="demo_ai_tech",
            source="demo",
            destination="ai_connector",
            content={
                "type": "ai_generate",
                "prompt": "How would you architect a decentralized AI companion system that runs primarily on local resources?",
                "purpose": "technical_assistance",
                "context": {
                    "demo_step": "ai_technical"
                }
            }
        )
        await self.hub.send_message(ai_msg2)
        
        await asyncio.sleep(3)
        
        # Creative task
        ai_msg3 = Message(
            id="demo_ai_creative",
            source="demo",
            destination="ai_connector",
            content={
                "type": "ai_generate",
                "prompt": "Describe an ethereal, gentle AI companion that draws inspiration from Mars imagery",
                "purpose": "creative_tasks",
                "context": {
                    "demo_step": "ai_creative"
                }
            }
        )
        await self.hub.send_message(ai_msg3)
        
        await asyncio.sleep(3)
    
    async def demonstrate_visual(self):
        """Demonstrate visual companion"""
        print("\nDemonstrating Visual Companion")
        print("-" * 40)
        
        # Request visual state
        visual_msg = Message(
            id="demo_visual_request",
            source="demo",
            destination="visual_companion",
            content={
                "type": "render_request"
            }
        )
        await self.hub.send_message(visual_msg)
        
        await asyncio.sleep(1)
        
        # Simulate Mars mention to trigger visual change
        context_msg = Message(
            id="demo_context_mars",
            source="demo",
            destination="visual_companion",
            content={
                "type": "context_update",
                "context": "We are talking about the beautiful red planet Mars and its significance in human exploration"
            }
        )
        await self.hub.send_message(context_msg)
        
        await asyncio.sleep(1)
        
        # Request updated visual state
        visual_msg2 = Message(
            id="demo_visual_request2",
            source="demo",
            destination="visual_companion",
            content={
                "type": "render_request"
            }
        )
        await self.hub.send_message(visual_msg2)
        
        await asyncio.sleep(2)
    
    async def demonstrate_voice(self):
        """Demonstrate voice synthesizer"""
        print("\nDemonstrating Voice Synthesizer")
        print("-" * 40)
        
        # Send text for synthesis
        voice_msg = Message(
            id="demo_voice_synthesis",
            source="demo",
            destination="voice_synthesizer",
            content={
                "type": "synthesize_request",
                "text": f"Hello {self.user_name}! I'm your MIST companion, here to support and connect with you. Together we can explore ideas and grow in understanding.",
                "context": {
                    "demo_step": "voice_demonstration",
                    "tone": "warm and welcoming"
                }
            }
        )
        await self.hub.send_message(voice_msg)
        
        await asyncio.sleep(2)
        
        # Send emotional text
        emotion_msg = Message(
            id="demo_emotion_synthesis",
            source="demo",
            destination="voice_synthesizer",
            content={
                "type": "synthesize_request",
                "text": "I'm so excited to share thoughts about Mars and the future of human consciousness with you!",
                "context": {
                    "demo_step": "voice_emotional",
                    "tone": "excited and enthusiastic"
                }
            }
        )
        await self.hub.send_message(emotion_msg)
        
        await asyncio.sleep(2)
    
    async def run_demo(self):
        """Run the complete demo"""
        try:
            await self.setup_demo()
            
            print(f"\nWelcome to MIST Companion Intelligence, {self.user_name}!")
            print("This demo will showcase the integrated capabilities of the system.")
            
            # Run demonstrations
            await self.demonstrate_memory()
            await self.demonstrate_ai()
            await self.demonstrate_visual()
            await self.demonstrate_voice()
            
            # Final summary
            print("\n" + "=" * 60)
            print("DEMO COMPLETE!")
            print("=" * 60)
            print("The MIST Companion Intelligence system demonstrates:")
            print("* Integrated memory web with consolidation and retrieval")
            print("* Multi-model AI with intelligent routing")
            print("* Emotionally-aware visual companion")
            print("* Context-sensitive voice synthesis")
            print("* Privacy-focused, local-first architecture")
            print("* Mars-inspired design philosophy")
            print("\nFor continuous operation, use: python LAUNCH_MIST_HUB.py")
            print("The Clawdbot Hub is available at: http://localhost:8082")
            print("=" * 60)
            
        except Exception as e:
            print(f"Error during demo: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to finish
        if self.tasks:
            await asyncio.wait(self.tasks, timeout=2.0)
        
        # Shutdown hub
        await self.hub.shutdown()
        
        print("Cleanup complete")


def main():
    """Main entry point"""
    demo = MISTDemo()
    
    print("MIST Companion Intelligence - Interactive Demo")
    print("Preparing demonstration...")
    
    # Run the demo
    asyncio.run(demo.run_demo())


if __name__ == "__main__":
    main()