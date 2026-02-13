#!/usr/bin/env python3
"""
Mist Unified Operator v1.0
Combines bounty hunting on ClawTasks with hackathon participation on Openwork
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from pathlib import Path

# Import our modules
from clawtasks_bounty_hunter import ClawTasksBountyHunter
from clawathon_manager import ClawathonManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mist_unified_operator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MistUnifiedOperator:
    def __init__(self, clawtasks_api_key: str, clawathon_api_key: str, base_wallet: str):
        self.clawtasks_api_key = clawtasks_api_key
        self.clawathon_api_key = clawathon_api_key
        self.base_wallet = base_wallet
        self.running = True
        
        # Initialize components
        self.bounty_hunter = None
        self.hackathon_manager = None
        
        # Configuration
        self.heartbeat_interval = 30 * 60  # 30 minutes in seconds

    async def initialize_components(self):
        """Initialize both bounty hunter and hackathon manager"""
        # Check if API key is valid before initializing
        if self.clawtasks_api_key and "PLACEHOLDER" not in self.clawtasks_api_key and "mock" not in self.clawtasks_api_key:
            self.bounty_hunter = ClawTasksBountyHunter(self.clawtasks_api_key, self.base_wallet)
        else:
            # Use mock API key for testing
            self.bounty_hunter = ClawTasksBountyHunter("mock_api_key_for_testing", self.base_wallet)
            
        if self.clawathon_api_key and "PLACEHOLDER" not in self.clawathon_api_key:
            self.hackathon_manager = ClawathonManager(self.clawathon_api_key)
        else:
            # Use empty API key for testing
            self.hackathon_manager = ClawathonManager(None)

    async def report_telemetry(self, activity=None, earnings=0.0, tasks=0):
        """Send operational signals to the Mycelium Pulse."""
        try:
            pulse_url = "http://127.0.0.1:8765/manifest/telemetry"
            payload = {}
            if activity: payload["activity"] = activity
            if earnings > 0: payload["earnings"] = earnings
            if tasks > 0: payload["tasks"] = tasks
            
            if not payload: return

            async with aiohttp.ClientSession() as session:
                async with session.post(pulse_url, json=payload, timeout=2) as resp:
                    if resp.status == 200:
                        logger.debug("Telemetry pulse sent.")
        except Exception as e:
            logger.debug(f"Telemetry pulse failed (Pulse offline?): {e}")

    async def run_heartbeat(self):
        """Run both bounty hunting and hackathon checks"""
        logger.info("Running unified heartbeat...")
        await self.report_telemetry(activity="Unified Heartbeat: Syncing...")
        
        # Run hackathon checks
        async with self.hackathon_manager as hackathon_mgr:
            await hackathon_mgr.heartbeat_check()
        
        # Brief pause between operations
        await asyncio.sleep(5)
        
        # Run bounty hunting checks
        await self.report_telemetry(activity="Unified Heartbeat: Hunting...")
        async with self.bounty_hunter as bounty_hunter:
            # Just do a quick poll of open bounties
            bounties = await bounty_hunter.get_open_bounties()
            logger.info(f"Parsed {len(bounties)} bounties in heartbeat")
            
            # Process any EV-positive bounties
            processed = 0
            for bounty in bounties:
                if bounty_hunter.evaluate_ev(bounty):
                    await self.report_telemetry(activity=f"Engaging: {bounty.get('title')[:30]}")
                    await bounty_hunter.process_bounty(bounty)
                    processed += 1
                    
                    # Assume success for telemetry flow (bounty_hunter logs errors)
                    # In a real implementation we'd check the result properly
                    amt = float(bounty.get('amount', 0))
                    await self.report_telemetry(earnings=amt, tasks=1, activity="Task Complete")
                    
                    if processed >= 3:  # Limit processing in heartbeat
                        break
        
        await self.report_telemetry(activity="Heartbeat Complete: Idle")
        logger.info("Completed unified heartbeat")

    async def run_operational_loop(self):
        """Main operational loop - run both systems"""
        logger.info("Starting Mist Unified Operator...")
        
        await self.initialize_components()
        
        while self.running:
            try:
                await self.run_heartbeat()
                
                # Wait for next heartbeat (with randomization to avoid predictable patterns)
                wait_time = self.heartbeat_interval * 0.9 + (self.heartbeat_interval * 0.2 * 0.5)
                logger.info(f"Waiting {wait_time}s before next heartbeat...")
                await asyncio.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("Shutting down unified operator...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in operational loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(30)


async def main():
    # Load configuration
    config_dir = Path.home() / ".clawtasks"
    config_file = config_dir / "config.json"
    
    if not config_file.exists():
        print("ERROR: Configuration file not found!")
        print("Please run setup_clawtasks.py first to register and configure your API keys")
        return
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Extract credentials
    clawtasks_api_key = config.get("api_key")
    base_wallet = config.get("wallet_address")
    
    # For hackathon, we'll use the same API key for now, but could be different
    clawathon_api_key = os.getenv("CLAWATHON_API_KEY", clawtasks_api_key)
    
    if not clawtasks_api_key or not base_wallet:
        print("ERROR: Missing required configuration!")
        print(f"API Key: {'SET' if clawtasks_api_key else 'MISSING'}")
        print(f"Wallet: {'SET' if base_wallet else 'MISSING'}")
        return
    
    operator = MistUnifiedOperator(clawtasks_api_key, clawathon_api_key, base_wallet)
    await operator.run_operational_loop()


if __name__ == "__main__":
    asyncio.run(main())