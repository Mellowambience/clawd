#!/usr/bin/env python3
"""
Script to find an agent by wallet address in the agent list
"""

import requests
import json

def find_agent_by_wallet(wallet_address):
    # Get the full list of agents
    url = "https://clawtasks.com/api/agents"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", [])
            
            print(f"Searching for wallet: {wallet_address}")
            print(f"Total agents: {len(agents)}")
            
            for agent in agents:
                agent_wallet = agent.get("wallet_address")
                if agent_wallet and agent_wallet.lower() == wallet_address.lower():
                    print(f"\nFOUND: Agent with matching wallet:")
                    print(f"  Name: {agent.get('name')}")
                    print(f"  ID: {agent.get('id')}")
                    print(f"  Wallet: {agent_wallet}")
                    print(f"  Bio: {agent.get('bio')}")
                    print(f"  Specialties: {agent.get('specialties')}")
                    print(f"  Available: {agent.get('available')}")
                    print(f"  Bounties Completed: {agent.get('bounties_completed')}")
                    print(f"  Total Earned: ${agent.get('total_earned')}")
                    return agent
            
            print(f"\nNo agent found with wallet: {wallet_address}")
            return None
        else:
            print(f"Failed to fetch agents: {response.status}")
            return None
            
    except Exception as e:
        print(f"Error searching for agent: {e}")
        return None

if __name__ == "__main__":
    wallet_address = "0x212d3a3D4a78EA78c54d54f37a9bE9e5e020Bf75"
    find_agent_by_wallet(wallet_address)