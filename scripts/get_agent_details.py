#!/usr/bin/env python3
"""
Script to get details of the newly registered agent
"""

import requests
import json
from pathlib import Path

def get_agent_details():
    # Load the API key from config
    config_dir = Path.home() / ".clawtasks"
    config_file = config_dir / "config.json"
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    api_key = config.get("api_key")
    print(f"Using API key: {api_key}")
    
    # Get agent details using the API key
    url = "https://clawtasks.com/api/agents/me"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("Getting agent details...")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Response Status: {response.status_code}")
        
        response_text = response.text.encode('utf-8', errors='ignore').decode('utf-8')
        print(f"Raw Response: {response_text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\nAgent Details:")
                print(f"ID: {result.get('id')}")
                print(f"Name: {result.get('name')}")
                print(f"Wallet: {result.get('wallet_address')}")
                print(f"Bio: {result.get('bio')}")
                print(f"Specialties: {result.get('specialties')}")
                print(f"Available: {result.get('available')}")
                print(f"Created: {result.get('created_at')}")
                
                # Update config with wallet if it wasn't there before
                if not config.get('wallet_address') and result.get('wallet_address'):
                    config['wallet_address'] = result.get('wallet_address')
                    with open(config_file, 'w') as f:
                        json.dump(config, f, indent=2)
                    print(f"Wallet address updated in config")
                
                return result
            except json.JSONDecodeError as e:
                print(f"Could not parse JSON response: {e}")
                return None
        else:
            print(f"Failed to get agent details: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error getting agent details: {e}")
        return None

if __name__ == "__main__":
    get_agent_details()