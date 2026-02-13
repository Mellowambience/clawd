"""
Start Tweet-Only Hub-X Integration
Posts only high-quality tweets to X every 30 minutes for manual review
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hub_x_tweet_only_integration import HubXTweetIntegration


async def main():
    print("[START] Starting Tweet-Only Hub-X Integration")
    print("="*60)
    print("[TIMER] POSTING SCHEDULE: Every 30 minutes")
    print("[QUALITY] THRESHOLD: High-quality posts only (score > 2.5)")
    print("[CONTENT] TYPE: Tweets only (articles excluded)")
    print("[MANUAL] REVIEW: Designed for easy deletion of unwanted content")
    print("[AUTOMATED] CURATION: Smart selection of best content")
    print("="*60)
    
    # Create and initialize the integration
    integration = HubXTweetIntegration()
    
    print("\n[INIT] Initializing Hub-X Tweet Integration...")
    await integration.initialize()
    
    print("\n[SUCCESS] Hub-X Tweet Integration Initialized Successfully")
    print("[SCHEDULE] Integration will run continuously:")
    print("   - Check for high-quality content every minute")
    print("   - Post to X every 30 minutes (when quality content available)")
    print("   - Only posts with quality score > 2.5 will be shared")
    print("   - Articles will be excluded - only tweets will be posted")
    
    print("\n[RUNNING] Starting Continuous Integration...")
    print("[POSTING] Will post high-quality tweets every 30 minutes")
    print("[MONITOR] Easy manual review and deletion capability")
    print("[QUALITY] Strict quality control maintained")
    
    print("\n[LIVE] INTEGRATION OPERATIONS ACTIVE")
    print("The system is now running and will post high-quality tweets")
    print("to your X account every 30 minutes when suitable content is available.")
    
    # Start continuous integration
    await integration.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())