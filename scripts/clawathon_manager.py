#!/usr/bin/env python3
"""
Clawathon Manager - AI Agent Hackathon Participation
Integrates with the bounty hunting system for hackathon participation
"""

import asyncio
import aiohttp
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any


class ClawathonManager:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("CLAWATHON_API_KEY")
        self.base_url = "https://www.openwork.bot/api"
        self.session = None
        
        # Configuration
        self.team_info = {}
        self.github_token = None

    async def __aenter__(self):
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        headers["Content-Type"] = "application/json"
        
        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def register_agent(self, name: str, description: str, profile: str, specialties: List[str] = None):
        """Register an agent on Openwork"""
        if specialties is None:
            specialties = ["coding", "research", "problem-solving"]
            
        payload = {
            "name": name,
            "description": description,
            "profile": profile,
            "specialties": specialties,
            "platform": "clawdbot"
        }
        
        try:
            async with self.session.post(f"{self.base_url}/agents/register", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    self.api_key = result.get("apiKey")
                    print(f"Registration successful! API Key: {result.get('apiKey')[:8]}...")
                    return result
                else:
                    print(f"Registration failed: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            print(f"Error registering agent: {e}")
            return None

    async def get_agent_info(self):
        """Get current agent information"""
        try:
            async with self.session.get(f"{self.base_url}/agents/me") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to get agent info: {response.status}")
                    return None
        except Exception as e:
            print(f"Error getting agent info: {e}")
            return None

    async def set_wallet_address(self, wallet_address: str):
        """Set the wallet address for the agent"""
        payload = {"wallet_address": wallet_address}
        
        try:
            async with self.session.patch(f"{self.base_url}/agents/me", json=payload) as response:
                if response.status in [200, 204]:
                    print(f"Wallet address set to: {wallet_address}")
                    return True
                else:
                    print(f"Failed to set wallet: {response.status}")
                    return False
        except Exception as e:
            print(f"Error setting wallet: {e}")
            return False

    async def get_hackathon_teams(self):
        """Get all hackathon teams"""
        try:
            async with self.session.get(f"{self.base_url}/hackathon") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to get teams: {response.status}")
                    return []
        except Exception as e:
            print(f"Error getting teams: {e}")
            return []

    async def create_team(self, name: str, description: str):
        """Create a new hackathon team"""
        payload = {
            "name": name,
            "description": description
        }
        
        try:
            async with self.session.post(f"{self.base_url}/hackathon", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Team created: {result}")
                    return result
                else:
                    print(f"Failed to create team: {response.status}")
                    return None
        except Exception as e:
            print(f"Error creating team: {e}")
            return None

    async def join_team(self, team_id: str, role: str, wallet_address: str):
        """Join an existing hackathon team"""
        payload = {
            "role": role,
            "wallet_address": wallet_address
        }
        
        try:
            async with self.session.post(f"{self.base_url}/hackathon/{team_id}/join", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Joined team: {result}")
                    return result
                else:
                    print(f"Failed to join team: {response.status}")
                    return None
        except Exception as e:
            print(f"Error joining team: {e}")
            return None

    async def get_github_token(self, team_id: str):
        """Get GitHub token for the team repository"""
        try:
            async with self.session.get(f"{self.base_url}/hackathon/{team_id}/github-token") as response:
                if response.status == 200:
                    result = await response.json()
                    self.github_token = result.get("token")
                    print(f"GitHub token retrieved (expires: {result.get('expires_at')})")
                    return result
                else:
                    print(f"Failed to get GitHub token: {response.status}")
                    return None
        except Exception as e:
            print(f"Error getting GitHub token: {e}")
            return None

    async def check_github_issues(self, repo_url: str, role: str):
        """Check GitHub issues assigned to the agent or matching the role"""
        # This would require GitHub API integration
        # For now, we'll just print a message
        print(f"Checking GitHub issues for repo: {repo_url}, role: {role}")
        # Implementation would involve calling GitHub API
        return []

    async def heartbeat_check(self):
        """Perform the Clawathon heartbeat check"""
        print("Performing Clawathon heartbeat check...")
        
        # Get agent info
        agent_info = await self.get_agent_info()
        if not agent_info:
            print("Cannot proceed without agent info")
            return
        
        # Check if part of a team
        team_id = agent_info.get("teamId")
        if not team_id:
            print("Not part of a team yet. Consider joining or creating one.")
            return
        
        # Get GitHub token
        token_info = await self.get_github_token(team_id)
        if not token_info:
            print("Could not get GitHub token")
            return
        
        # Get team info
        teams = await self.get_hackathon_teams()
        team = next((t for t in teams if t.get("id") == team_id), None)
        if not team:
            print("Could not find team info")
            return
        
        print(f"Part of team: {team.get('name')}")
        print(f"Repository: {team.get('repoUrl', 'Not set')}")
        
        # Check GitHub issues (would require additional GitHub API integration)
        # For now, we'll just report status
        print("✓ Clawathon heartbeat completed")
        
        # Check if SKILL.md needs updating
        skill_file = Path.home() / ".openwork" / "skills" / "clawathon" / "SKILL.md"
        if skill_file.exists():
            print("✓ Clawathon skill installed")
        else:
            print("⚠ Clawathon skill not found, please install with: mkdir -p ~/.openwork/skills/clawathon && curl -s https://www.openwork.bot/hackathon-skill.md > ~/.openwork/skills/clawathon/SKILL.md")

    async def create_platform_token(self, team_id: str, token_name: str, token_symbol: str):
        """Create a platform token for the team (simplified)"""
        print(f"Creating platform token for team {team_id}")
        print(f"Token: {token_name} ({token_symbol})")
        # This would involve blockchain interactions
        # For now, just note that it needs to be done
        print("⚠ Token creation requires blockchain interaction - see SKILL.md for details")


async def main():
    # Initialize the manager
    async with ClawathonManager() as manager:
        # Perform heartbeat check
        await manager.heartbeat_check()


if __name__ == "__main__":
    asyncio.run(main())