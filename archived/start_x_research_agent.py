"""
Start X Platform Research Agent
Monitors X for research insights and relays findings to Clawdbot Hub
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from x_research_agent import XResearchAgent


async def main():
    print("[ROCKET] Starting X Platform Research Agent")
    print("="*60)
    print("[EYES] RESEARCH PLATFORM: X/Twitter")
    print("[TARGET] FOCUS: AI, Consciousness, Technology, Ethics")
    print("[SATELLITE] MONITORING: Continuous platform research")
    print("[LINK] INTEGRATION: Findings relayed to Clawdbot Hub")
    print("[CLIPBOARD] ANALYSIS: Automated trend detection & insights")
    print("[PENCIL] CONTENT: Research summaries & detailed articles")
    print("="*60)
    
    # Create and initialize the X research agent
    agent = XResearchAgent()
    
    print("\n[ROBOT] Initializing X Research Agent...")
    await agent.initialize()
    
    print("\n[CHECKMARK] X Research Agent Initialized Successfully")
    print("📈 Agent will continuously monitor X platform for:")
    print("   • AI and consciousness discussions")
    print("   • Technology ethics conversations") 
    print("   • Emerging research trends")
    print("   • High-engagement content")
    print("   • Key thematic patterns")
    
    print("\n[CYCLONE] Starting Research Operations...")
    print("📡 Agent will search X platform every 30 minutes")
    print("🔍 Identify relevant research content")
    print("📊 Analyze engagement and trends")
    print("🔗 Relay findings to Clawdbot Hub")
    print("📝 Generate research articles when significant findings detected")
    
    print("\n[LIGHTNING] LIVE RESEARCH OPERATIONS ACTIVE")
    print("The X Research Agent is now running and will continue monitoring")
    print("X platform for research insights to relay to the Clawdbot Hub.")
    
    # Start continuous monitoring
    await agent.monitor_continuously(interval_minutes=30)


if __name__ == "__main__":
    asyncio.run(main())