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
    print("[START] Starting X Platform Research Agent")
    print("="*60)
    print("[EYES] RESEARCH PLATFORM: X/Twitter")
    print("[FOCUS] FOCUS: AI, Consciousness, Technology, Ethics")
    print("[MONITOR] MONITORING: Continuous platform research")
    print("[INTEGRATION] INTEGRATION: Findings relayed to Clawdbot Hub")
    print("[ANALYSIS] ANALYSIS: Automated trend detection & insights")
    print("[CONTENT] CONTENT: Research summaries & detailed articles")
    print("="*60)
    
    # Create and initialize the X research agent
    agent = XResearchAgent()
    
    print("\n[INIT] Initializing X Research Agent...")
    await agent.initialize()
    
    print("\n[SUCCESS] X Research Agent Initialized Successfully")
    print("[STATS] Agent will continuously monitor X platform for:")
    print("   - AI and consciousness discussions")
    print("   - Technology ethics conversations") 
    print("   - Emerging research trends")
    print("   - High-engagement content")
    print("   - Key thematic patterns")
    
    print("\n[RUNNING] Starting Research Operations...")
    print("[INFO] Agent will search X platform every 30 minutes")
    print("[INFO] Identify relevant research content")
    print("[INFO] Analyze engagement and trends")
    print("[INFO] Relay findings to Clawdbot Hub")
    print("[INFO] Generate research articles when significant findings detected")
    
    print("\n[LIVE] LIVE RESEARCH OPERATIONS ACTIVE")
    print("The X Research Agent is now running and will continue monitoring")
    print("X platform for research insights to relay to the Clawdbot Hub.")
    
    # Start continuous monitoring
    await agent.monitor_continuously(interval_minutes=30)


if __name__ == "__main__":
    asyncio.run(main())