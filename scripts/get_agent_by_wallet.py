#!/usr/bin/env python3
"""
Script to get agent by wallet address on ClawTasks
"""

import requests
import json

def get_agent_by_wallet():
    wallet_address = "0x212d3a3D4a78EA78c54d54f37a9bE9e5e020Bf75"
    url = f"https://clawtasks.com/api/agents/by-wallet/{wallet_address}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Attempting to get agent by wallet: {wallet_address}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Agent found: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"Request failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error getting agent: {e}")
        return None

if __name__ == "__main__":
    get_agent_by_wallet()