#!/usr/bin/env python3
"""
Debug script to check the actual bounty API response structure
"""

import requests
import json

def debug_bounties():
    # Use the API key from config
    from pathlib import Path
    
    config_dir = Path.home() / ".clawtasks"
    config_file = config_dir / "config.json"
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    api_key = config.get("api_key")
    
    print(f"Using API key: {api_key[:8]}..." if api_key else "No API key found")
    
    # Get bounties
    url = "https://clawtasks.com/api/bounties?status=open"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("Fetching bounties...")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            print(f"Response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict) and 'bounties' in data:
                bounties = data['bounties']
                print(f"Number of bounties: {len(bounties)}")
                
                if bounties:
                    print(f"First bounty keys: {bounties[0].keys() if isinstance(bounties[0], dict) else 'Not a dict'}")
                    print(f"First bounty: {json.dumps(bounties[0], indent=2)[:500]}...")
                    
                    # Check for any None values
                    for i, bounty in enumerate(bounties):
                        if bounty is None:
                            print(f"Bounty {i} is None!")
                        elif isinstance(bounty, dict):
                            for key, value in bounty.items():
                                if value is None:
                                    print(f"Bounty {i} has None value for key '{key}'")
            
            else:
                print(f"Unexpected response structure: {data}")
                
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_bounties()