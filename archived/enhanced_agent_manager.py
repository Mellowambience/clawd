"""
Enhanced Agent Manager for Clawdbot Hub
Manages the enhanced specialized agents with improved quality controls
"""

import asyncio
import signal
import sys
from typing import Dict, List
from enhanced_specialized_agents import (
    EnhancedPhilosopherAgent, EnhancedTechnologistAgent, 
    EnhancedExplorerAgent, EnhancedHarmonyAgent, EnhancedSynthesisAgent
)


class EnhancedAgentManager:
    """Manages enhanced agents for the Clawdbot Hub with improved quality focus"""
    
    def __init__(self, hub_url: str = "http://localhost:8082"):
        self.hub_url = hub_url
        self.agents = {}
        self.running = False
        self.shutdown_event = asyncio.Event()

    async def create_agents(self):
        """Create and register enhanced agents with research methodology focus"""
        agent_classes = [
            EnhancedPhilosopherAgent,
            EnhancedTechnologistAgent,
            EnhancedExplorerAgent,
            EnhancedHarmonyAgent,
            EnhancedSynthesisAgent
        ]
        
        for agent_class in agent_classes:
            agent = agent_class(self.hub_url)
            self.agents[agent.name] = agent
            print(f"Created enhanced agent: {agent.name} with role: {agent.role}")
        
        print(f"Created {len(self.agents)} enhanced agents with research methodology focus")

    async def initialize_agents(self):
        """Initialize all agents"""
        for name, agent in self.agents.items():
            await agent.initialize()
            print(f"Initialized enhanced agent: {name}")

    async def start_all_agents(self):
        """Start all agents concurrently"""
        if not self.agents:
            print("No agents registered to start")
            return

        self.running = True
        print("Starting all enhanced agents...")
        
        # Create tasks for all agents
        tasks = []
        for name, agent in self.agents.items():
            task = asyncio.create_task(self.run_agent(agent))
            tasks.append(task)
        
        print("All enhanced agents started successfully!")
        print("Agents now operating with research methodology and truth-seeking focus!")
        
        # Wait for all tasks (they run indefinitely)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def run_agent(self, agent):
        """Run a single agent's monitoring loop"""
        try:
            await agent.monitor_hub()
        except Exception as e:
            print(f"Error running agent {agent.name}: {e}")
        finally:
            await agent.stop()

    async def stop_all_agents(self):
        """Stop all agents gracefully"""
        self.running = False
        print("Stopping all agents...")
        
        for name, agent in self.agents.items():
            await agent.stop()
        
        print("All enhanced agents stopped")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down enhanced agents...")
        self.shutdown_event.set()

    async def run(self):
        """Main run method"""
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("Initializing Enhanced Clawdbot Hub Agents with Research Methodology Focus...")
        
        # Create agents
        await self.create_agents()
        
        # Initialize agents
        await self.initialize_agents()
        
        print("Starting enhanced agents...")
        
        # Start all agents
        await self.start_all_agents()
        
        # Wait for shutdown signal
        await self.shutdown_event.wait()
        
        print("\nShutting down enhanced agents...")
        await self.stop_all_agents()
        print("All enhanced agents stopped. Goodbye!")


async def main():
    manager = EnhancedAgentManager()
    await manager.run()


if __name__ == "__main__":
    asyncio.run(main())