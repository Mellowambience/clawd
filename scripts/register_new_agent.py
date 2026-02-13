#!/usr/bin/env python3
"""
Script to register a new agent without specifying wallet (let system generate)
"""

import requests
import json

def register_without_wallet():
    url = "https://clawtasks.com/api/agents"
    
    # Register without wallet address to let system generate one
    payload = {
        "name": "mistnewagent"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Attempting to register agent without wallet address...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Registration successful!")
            print(f"API Key: {result.get('api_key', 'NOT FOUND')}")
            print(f"Wallet: {result.get('wallet', {}).get('address', 'NOT FOUND')}")
            return result
        else:
            print(f"Registration failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error during registration: {e}")
        return None

if __name__ == "__main__":
    register_without_wallet()