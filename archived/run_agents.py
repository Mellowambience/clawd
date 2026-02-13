"""
Runner script to start the Clawdbot Hub agents
"""

import asyncio
import signal
import sys
from clawdbot_agents.agent_manager import AgentManager


class AgentRunner:
    """Responsible for running agents with proper shutdown handling"""
    
    def __init__(self):
        self.manager = AgentManager()
        self.shutdown_event = asyncio.Event()
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down agents...")
        self.shutdown_event.set()
    
    async def run(self):
        """Main run method"""
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("Initializing Clawdbot Hub Agents...")
        
        # Create and register default agents
        agents = self.manager.create_default_agents()
        
        for agent in agents:
            await self.manager.register_agent(agent)
        
        print(f"Registered {len(self.manager.agents)} agents")
        
        # Initialize all agents
        await self.manager.initialize_agents()
        
        print("Starting agents...")
        
        # Create tasks for all agents
        tasks = []
        for name, agent in self.manager.agents.items():
            task = asyncio.create_task(self.run_single_agent(agent))
            tasks.append(task)
        
        print("Agents are now active and monitoring the Clawdbot Hub!")
        print("Press Ctrl+C to stop the agents.")
        
        # Wait for shutdown signal
        await self.shutdown_event.wait()
        
        print("\nShutting down agents...")
        await self.manager.stop_all_agents()
        print("All agents stopped. Goodbye!")
    
    async def run_single_agent(self, agent):
        """Run a single agent with error handling"""
        try:
            await agent.monitor_hub()
        except Exception as e:
            agent.logger.error(f"Error in agent {agent.name}: {e}")
        finally:
            await agent.stop()


async def main():
    runner = AgentRunner()
    await runner.run()


if __name__ == "__main__":
    asyncio.run(main())