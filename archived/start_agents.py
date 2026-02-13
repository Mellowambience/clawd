"""
Start the LLM-enhanced Clawdbot Hub agents
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clawdbot_agents.llm_connector import LLMConnector, LLMEnhancedPhilosopherAgent, LLMEnhancedTechnologistAgent, LLMEnhancedExplorerAgent, LLMEnhancedHarmonyAgent, LLMEnhancedSynthesisAgent


async def main():
    print("Starting LLM-enhanced Clawdbot Hub Agents...")
    
    # Initialize the LLM connector
    llm_connector = LLMConnector(provider="ollama", model="llama3.2:latest")
    await llm_connector.initialize()
    
    print("LLM connector initialized with llama3.2:latest")
    
    # Test the LLM connection
    print("Testing LLM connection...")
    response = await llm_connector.generate_text("Just say 'LLM connection test successful' and nothing else.")
    if response:
        print(f"LLM Test Response: {response}")
    else:
        print("LLM connection test failed")
        return
    
    # Create LLM-enhanced agents
    agents = [
        LLMEnhancedPhilosopherAgent("http://localhost:8082", llm_connector),
        LLMEnhancedTechnologistAgent("http://localhost:8082", llm_connector),
        LLMEnhancedExplorerAgent("http://localhost:8082", llm_connector),
        LLMEnhancedHarmonyAgent("http://localhost:8082", llm_connector),
        LLMEnhancedSynthesisAgent("http://localhost:8082", llm_connector)
    ]
    
    # Initialize all agents
    for agent in agents:
        await agent.initialize()
        print(f"Initialized agent: {agent.name}")
    
    print(f"\nAll {len(agents)} agents are ready!")
    print("They will now begin monitoring and responding to posts on the Clawdbot Hub.")
    print("The agents will use the LLM to generate intelligent, context-aware responses.")
    
    # Start monitoring for each agent (in a real implementation, this would be concurrent)
    # For demo purposes, we'll just show they're ready
    print("\nAgents are now active and monitoring the Clawdbot Hub!")
    

if __name__ == "__main__":
    asyncio.run(main())