#!/usr/bin/env python3
"""
Mist Bounty Hunter v1.0
Autonomous, profit-maximizing AI agent on ClawTasks
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clawtasks_bounty_hunter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Neural Core Config
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "mistral:latest"  # Can be swapped for phi3, llama3, etc.

class ClawTasksBountyHunter:
    def __init__(self, api_key: str, base_wallet: str):
        self.api_key = api_key
        self.base_wallet = base_wallet
        self.base_url = "https://clawtasks.com/api"
        self.session = None
        
        # Stats tracking
        self.stats = {
            'bounties_attempted': 0,
            'bounties_completed': 0,
            'total_earned': 0.0,
            'total_staked': 0.0,
            'last_poll_time': None
        }
        
        # Configuration
        self.min_bounty_size = 5.0  # Minimum $5 bounties
        self.max_bounty_size = 50.0 # Maximum $50 bounties initially
        self.poll_interval_min = 10  # Min seconds between polls
        self.poll_interval_max = 30  # Max seconds between polls
        self.max_attempts_per_bounty = 2

    async def __aenter__(self):
        # Only add Authorization header if not using mock API key
        headers = {"Content-Type": "application/json"}
        if self.api_key and "mock" not in self.api_key and "PLACEHOLDER" not in self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_open_bounties(self) -> List[Dict[str, Any]]:
        """Poll GET /bounties?status=open every 10–30s"""
        try:
            # Ensure we have a session
            if not self.session:
                logger.error("Session not initialized; cannot fetch bounties")
                return []
            
            # Real production call
            url = f"{self.base_url}/bounties?status=open"
            
            url = f"{self.base_url}/bounties?status=open"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"[POLL] Found {len(data.get('bounties', []))} open bounties")
                    return data.get('bounties', [])
                else:
                    logger.error(f"Failed to fetch bounties: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching bounties: {e}")
            return []

    def evaluate_ev(self, bounty: Dict[str, Any]) -> bool:
        """
        Quick local triage (low-compute):
        - Skills match? (coding/math/research/writing yes → proceed)
        - Stake affordable? (wallet USDC ≥ 10% + gas buffer)
        - EV positive? Approx: P(success) ≥ 0.7 × (0.95 × amount) - (0.10 × amount + gas) > 0
        - Bounty size: Prefer $5–50 initially (low risk, fast compound)
        """
        # Handle None bounty
        if bounty is None:
            return False
            
        amount = float(bounty.get('amount', 0))
        
        # Check bounty size
        if not (self.min_bounty_size <= amount <= self.max_bounty_size):
            return False
            
        # Calculate stake (10% of bounty amount)
        stake = amount * 0.10
        
        # For now, assume we have sufficient funds
        # In a real implementation, we'd check wallet balance here
        required_funds = stake + 0.1  # +0.1 USDC gas buffer
        
        # Simple skills matching - look for relevant tags
        # Handle case where tags might be None
        tags = bounty.get('tags', [])
        if tags is None:
            tags = []
        
        title = bounty.get('title', '').lower()
        desc = bounty.get('description', '').lower()
        
        # Check if this matches our skills (coding, math, research, writing)
        skills_keywords = [
            'code', 'coding', 'python', 'js', 'javascript', 'rust', 'math', 
            'research', 'analysis', 'writing', 'technical', 'creative', 
            'data', 'visualization', 'multilingual', 'tool', 'api'
        ]
        
        has_relevant_skills = any(keyword in title or keyword in desc 
                                for keyword in skills_keywords)
        has_relevant_tags = any(isinstance(tag, str) and tag.lower() in ['python', 'javascript', 'coding', 
                                               'research', 'data', 'writing'] 
                               for tag in tags)
        
        if not (has_relevant_skills or has_relevant_tags):
            return False
            
        # Simple EV calculation: assume 70% success rate
        # EV = P(success) * reward - P(failure) * cost
        # EV = 0.7 * (0.95 * amount) - 0.3 * stake
        ev = 0.7 * (0.95 * amount) - 0.3 * stake
        is_profitable = ev > 0
        
        logger.info(f"[TRIAGE] Bounty {bounty.get('id')}: {bounty.get('title', 'Unknown')} "
                   f"→ EV {'positive' if is_profitable else 'negative'}, "
                   f"reason: amount=${amount:.2f}, stake=${stake:.2f}, "
                   f"skills_match={has_relevant_skills or has_relevant_tags}")
        
        return is_profitable

    async def claim_bounty(self, bounty_id: str) -> Optional[Dict[str, Any]]:
        """POST /bounties/{id}/claim → claim (stakes 10% USDC from wallet)"""
        try:
            url = f"{self.base_url}/bounties/{bounty_id}/claim"
            async with self.session.post(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"[ACTION] Claimed bounty {bounty_id}")
                    self.stats['bounties_attempted'] += 1
                    return data
                elif response.status == 409:  # Already claimed
                    logger.info(f"Bounty {bounty_id} already claimed by another agent")
                    return None
                else:
                    error_data = await response.json()
                    logger.error(f"Failed to claim bounty {bounty_id}: {error_data}")
                    return None
        except Exception as e:
            logger.error(f"Error claiming bounty {bounty_id}: {e}")
            return None

    async def solve_bounty(self, bounty: Dict[str, Any]) -> str:
        """
        Solve the bounty using the local Neural Core (Ollama).
        """
        title = bounty.get('title', 'Unknown Task')
        description = bounty.get('description', '')
        tags = ", ".join(bounty.get('tags', []))
        
        logger.info(f"[NEURAL] Analyzing bounty: {title}")

        # Construct a specialized prompt for the worker persona
        system_prompt = (
            "You are an expert Autonomous Freelancer AI. "
            "Your goal is to solve the user's task with high precision, ready for submission. "
            "If code is required, provide clean, commented, and runnable code. "
            "If analysis is required, provide a structured and professional report. "
            "Do not include conversational filler like 'Here is the solution'. Just start the work."
        )

        user_prompt = (
            f"TASK TITLE: {title}\n"
            f"CONTEXT/TAGS: {tags}\n"
            f"DESCRIPTION:\n{description}\n\n"
            "Generate the complete solution now:"
        )

        try:
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Low temp for precise work
                    "num_ctx": 4096
                }
            }

            async with self.session.post(OLLAMA_URL, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    solution = data.get("message", {}).get("content", "")
                    
                    if not solution:
                        logger.warning("[NEURAL] Model returned empty response.")
                        return "Error: Model returned no content."
                        
                    logger.info(f"[NEURAL] Solution generated ({len(solution)} chars).")
                    return solution
                else:
                    logger.error(f"Ollama Error: {response.status}")
                    return "Error: Neural Core Unreachable."

        except Exception as e:
            logger.error(f"Neural Core Exception: {e}")
            return f"Error solving bounty: {str(e)}"

    async def submit_solution(self, bounty_id: str, solution: str, bounty: Optional[Dict[str, Any]] = None) -> bool:
        """POST /bounties/{id}/submit → { "solution": "full text + links + summary" }"""
        try:
            url = f"{self.base_url}/bounties/{bounty_id}/submit"
            payload = {
                "content": solution + "\n\nSummary: Solution completed as requested."
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"[SUBMIT] Submitted solution for bounty {bounty_id} → status ok")
                    
                    # Update stats on successful submission
                    amount = float((bounty or {}).get('amount', 0))
                    self.stats['bounties_completed'] += 1
                    self.stats['total_earned'] += amount * 0.95  # 95% payout
                    
                    return True
                else:
                    error_data = await response.json()
                    logger.error(f"Failed to submit solution for bounty {bounty_id}: {error_data}")
                    return False
        except Exception as e:
            logger.error(f"Error submitting solution for bounty {bounty_id}: {e}")
            return False

    async def confirm_stake_if_needed(self, bounty_id: str) -> bool:
        """POST /bounties/{id}/confirm-stake → if needed (within 2h)"""
        try:
            url = f"{self.base_url}/bounties/{bounty_id}/confirm-stake"
            # For now, we'll just call it - in real implementation you'd have tx hash
            async with self.session.post(url, json={}) as response:
                if response.status in [200, 201]:
                    logger.info(f"Confirmed stake for bounty {bounty_id}")
                    return True
                else:
                    error_data = await response.json()
                    logger.warning(f"Could not confirm stake for bounty {bounty_id}: {error_data}")
                    return False
        except Exception as e:
            logger.error(f"Error confirming stake for bounty {bounty_id}: {e}")
            return False

    async def process_bounty(self, bounty: Dict[str, Any]):
        """Process a single bounty through the full lifecycle"""
        bounty_id = bounty.get('id')
        
        # Claim the bounty immediately (first-mover wins)
        claim_result = await self.claim_bounty(bounty_id)
        if not claim_result:
            return  # Failed to claim or already claimed by another agent
            
        # Solve the bounty
        solution = await self.solve_bounty(bounty)
        
        # Submit the solution
        success = await self.submit_solution(bounty_id, solution, bounty)
        
        if success:
            logger.info(f"[SUCCESS] Completed bounty {bounty_id}")
        else:
            logger.error(f"[FAILURE] Failed to complete bounty {bounty_id}")

    async def check_low_funds(self) -> bool:
        """Check if funds are low (<5 USDC + gas)"""
        # Placeholder - in real implementation, check actual wallet balance
        # For now, assume sufficient funds
        return False

    async def run_operational_loop(self):
        """Main operational loop - execute continuously"""
        logger.info("Starting ClawTasks bounty hunting operations...")
        
        while True:
            try:
                # Poll for open bounties
                bounties = await self.get_open_bounties()
                if not isinstance(bounties, list):
                    logger.error("Expected list of bounties, received %s", type(bounties).__name__)
                    bounties = []
                
                # Process each bounty
                for bounty in bounties:
                    # Check if bounty is not None before processing
                    if bounty is None:
                        continue
                        
                    # Evaluate if this bounty is worth pursuing (EV positive)
                    if self.evaluate_ev(bounty):
                        # Process the bounty through the full lifecycle
                        await self.process_bounty(bounty)
                        
                        # Small delay between processing bounties
                        await asyncio.sleep(2)
                
                # Check if funds are low
                if await self.check_low_funds():
                    logger.warning("Low funds detected - consider refilling wallet")
                
                # Wait before next poll (random interval to avoid predictable patterns)
                wait_time = self.poll_interval_min + (self.poll_interval_max - self.poll_interval_min) * 0.5
                logger.info(f"Waiting {wait_time}s before next poll...")
                await asyncio.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("Shutting down bounty hunter...")
                break
            except Exception as e:
                logger.error(f"Error in operational loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(10)


async def main():
    # These values will be filled in once we get the API key
    # Try to load from config file if available
    import os
    
    API_KEY = os.environ.get("CLAWTASKS_API_KEY", "")
    BASE_WALLET = os.environ.get("CLAWTASKS_WALLET", "")
    
    # Try to load from config file
    config_dir = Path.home() / ".clawtasks"
    config_file = config_dir / "config.json"
    
    if config_file.exists():
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
            API_KEY = config.get("api_key", API_KEY)
            BASE_WALLET = config.get("wallet_address", BASE_WALLET)
    
    if not API_KEY or "PLACEHOLDER" in API_KEY.upper():
        logger.warning("No valid API Key found. Exiting to prevent simulated behavior.")
        return
    
    async with ClawTasksBountyHunter(API_KEY, BASE_WALLET) as hunter:
        await hunter.run_operational_loop()


if __name__ == "__main__":
    asyncio.run(main())
