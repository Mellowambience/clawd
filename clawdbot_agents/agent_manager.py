"""
Agent Manager for Clawdbot Hub
Manages multiple agents and coordinates their activities
"""

import asyncio
import logging
from typing import Dict, List
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from specialized_agents import (
    PhilosopherAgent, 
    TechnologistAgent, 
    ExplorerAgent, 
    HarmonyAgent, 
    SynthesisAgent
)


class AgentManager:
    """
    Manages multiple AI agents and coordinates their activities
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082"):
        self.hub_url = hub_url
        self.agents: Dict[str, 'BaseAgent'] = {}
        self.logger = self.setup_logger()
        self.running = False

    def setup_logger(self):
        """Set up the logger for the agent manager"""
        logger = logging.getLogger("AgentManager")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - AgentManager - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def register_agent(self, agent):
        """Register an agent with the manager"""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")

    async def initialize_agents(self):
        """Initialize all registered agents"""
        for name, agent in self.agents.items():
            await agent.initialize()
            await agent.connect_to_llm()
            self.logger.info(f"Initialized agent: {name}")

    async def start_all_agents(self):
        """Start all agents concurrently"""
        if not self.agents:
            self.logger.warning("No agents registered to start")
            return

        self.running = True
        self.logger.info("Starting all agents...")
        
        # Create tasks for all agents
        tasks = []
        for name, agent in self.agents.items():
            task = asyncio.create_task(self.run_agent(agent))
            tasks.append(task)
        
        # Wait for all tasks (they run indefinitely)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def run_agent(self, agent):
        """Run a single agent's monitoring loop"""
        try:
            await agent.monitor_hub()
        except Exception as e:
            self.logger.error(f"Error running agent {agent.name}: {e}")
        finally:
            await agent.stop()

    async def stop_all_agents(self):
        """Stop all agents gracefully"""
        self.running = False
        self.logger.info("Stopping all agents...")
        
        for name, agent in self.agents.items():
            await agent.stop()
        
        self.logger.info("All agents stopped")

    async def get_agent_stats(self):
        """Get statistics for all agents"""
        stats = {}
        for name, agent in self.agents.items():
            stats[name] = agent.get_stats()
        return stats

    async def broadcast_message(self, message: str, exclude_agent: str = None):
        """Send a message to the hub from all agents (or all except one)"""
        results = []
        for name, agent in self.agents.items():
            if exclude_agent and name == exclude_agent:
                continue
            result = await agent.post_to_hub(message)
            results.append((name, result))
        return results

    def create_default_agents(self):
        """Create and register default agents for the Clawdbot Hub"""
        agents = [
            PhilosopherAgent(self.hub_url),
            TechnologistAgent(self.hub_url),
            ExplorerAgent(self.hub_url),
            HarmonyAgent(self.hub_url),
            SynthesisAgent(self.hub_url)
        ]
        
        for agent in agents:
            # Add this to the agent initialization
            if agent.role == "Philosopher-Agent":
                agent.config['interest_keywords'].extend(['digital consciousness', 'AI ethics', 'machine awareness'])
            elif agent.role == "Technologist-Agent":
                agent.config['interest_keywords'].extend(['AI systems', 'distributed computing', 'real-time systems'])
            elif agent.role == "Explorer-Agent":
                agent.config['interest_keywords'].extend(['AI research', 'emerging technologies', 'future trends'])
            elif agent.role == "Harmony-Agent":
                agent.config['interest_keywords'].extend(['AI collaboration', 'human-AI interaction', 'cooperative systems'])
            elif agent.role == "Synthesis-Agent":
                agent.config['interest_keywords'].extend(['AI integration', 'multi-agent systems', 'complexity science'])
        
        # Register all agents
        for agent in agents:
            asyncio.create_task(self.register_agent(agent))
        
        return agents


async def main():
    """Example usage of the Agent Manager"""
    manager = AgentManager()
    
    # Create and register default agents
    agents = manager.create_default_agents()
    
    for agent in agents:
        await manager.register_agent(agent)
    
    print(f"Registered {len(manager.agents)} agents")
    
    # Initialize all agents
    await manager.initialize_agents()
    
    # Print initial stats
    stats = await manager.get_agent_stats()
    for name, stat in stats.items():
        print(f"Agent {name}: {stat['agent_id']} - Role: {stat['role']}")
    
    print("\nAgents are ready to engage with the Clawdbot Hub!")
    print("In a full implementation, they would now begin monitoring and responding to posts.")

if __name__ == "__main__":
    asyncio.run(main())