"""
Runner script for LLM-enhanced Clawdbot Hub agents
"""

import asyncio
import signal
import sys
from clawdbot_agents.llm_connector import LLMConnector, LLMEnhancedPhilosopherAgent, LLMEnhancedTechnologistAgent, LLMEnhancedExplorerAgent, LLMEnhancedHarmonyAgent, LLMEnhancedSynthesisAgent


class LLMEnhancedAgentManager:
    """Manages LLM-enhanced agents for the Clawdbot Hub"""
    
    def __init__(self, hub_url: str = "http://localhost:8082", llm_provider: str = "ollama", llm_model: str = "llama3.3"):
        self.hub_url = hub_url
        self.llm_connector = LLMConnector(provider=llm_provider, model=llm_model)
        self.agents = {}
        self.running = False
        self.shutdown_event = asyncio.Event()

    async def initialize(self):
        """Initialize the LLM connector and agents"""
        await self.llm_connector.initialize()
        print("LLM connector initialized")

    async def create_agents(self):
        """Create and register LLM-enhanced agents"""
        agents = [
            LLMEnhancedPhilosopherAgent(self.hub_url, self.llm_connector),
            LLMEnhancedTechnologistAgent(self.hub_url, self.llm_connector),
            LLMEnhancedExplorerAgent(self.hub_url, self.llm_connector),
            LLMEnhancedHarmonyAgent(self.hub_url, self.llm_connector),
            LLMEnhancedSynthesisAgent(self.hub_url, self.llm_connector)
        ]
        
        for agent in agents:
            self.agents[agent.name] = agent
            print(f"Created agent: {agent.name} with role: {agent.role}")
        
        print(f"Created {len(self.agents)} LLM-enhanced agents")

    async def initialize_agents(self):
        """Initialize all agents"""
        for name, agent in self.agents.items():
            await agent.initialize()
            print(f"Initialized agent: {name}")

    async def start_all_agents(self):
        """Start all agents concurrently"""
        if not self.agents:
            print("No agents registered to start")
            return

        self.running = True
        print("Starting all agents...")
        
        # Create tasks for all agents
        tasks = []
        for name, agent in self.agents.items():
            task = asyncio.create_task(self.run_agent(agent))
            tasks.append(task)
        
        print("All agents started successfully!")
        
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
        
        await self.llm_connector.close()
        print("All agents and LLM connector stopped")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down agents...")
        self.shutdown_event.set()

    async def run(self):
        """Main run method"""
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("Initializing LLM-enhanced Clawdbot Hub Agents...")
        
        # Initialize LLM connector
        await self.initialize()
        
        # Create agents
        await self.create_agents()
        
        # Initialize agents
        await self.initialize_agents()
        
        print("Starting agents...")
        
        # Start all agents
        await self.start_all_agents()
        
        # Wait for shutdown signal
        await self.shutdown_event.wait()
        
        print("\nShutting down agents...")
        await self.stop_all_agents()
        print("All agents stopped. Goodbye!")


async def main():
    manager = LLMEnhancedAgentManager()
    await manager.run()


if __name__ == "__main__":
    asyncio.run(main())