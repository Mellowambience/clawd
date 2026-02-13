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
        "name": "mistnewagent001"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Attempting to register agent without wallet address...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Response Status: {response.status_code}")
        
        # Handle response text more carefully
        try:
            response_text = response.text.encode('utf-8', errors='ignore').decode('utf-8')
            print(f"Response Text: {response_text}")
        except:
            print("Could not decode response text")
        
        if response.status_code == 201:
            try:
                result = response.json()
                print(f"Registration successful!")
                print(f"API Key: {result.get('api_key', 'NOT FOUND')}")
                print(f"Wallet: {result.get('wallet', {}).get('address', 'NOT FOUND')}")
                
                # Save the result to our config
                import os
                from pathlib import Path
                
                config_dir = Path.home() / ".clawtasks"
                config_dir.mkdir(exist_ok=True)
                
                config = {
                    "api_key": result.get('api_key'),
                    "wallet_address": result.get('wallet', {}).get('address'),
                    "agent_name": "mistnewagent",
                    "created_at": result.get('created_at')
                }
                
                config_file = config_dir / "config.json"
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                
                print(f"Configuration saved to {config_file}")
                
                # Also update .env
                env_file = Path.cwd() / ".env"
                with open(env_file, 'a') as f:
                    f.write(f"\n# ClawTasks Configuration (NEWLY REGISTERED)\n")
                    f.write(f"CLAWTASKS_API_KEY={config['api_key']}\n")
                    f.write(f"CLAWTASKS_WALLET={config['wallet_address']}\n")
                    f.write(f"CLAWTASKS_AGENT_NAME=mistnewagent\n")
                
                print(f"Environment variables updated in {env_file}")
                
                return result
            except json.JSONDecodeError:
                print("Could not parse JSON response")
                return None
        else:
            print(f"Registration failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error during registration: {e}")
        return None

if __name__ == "__main__":
    register_without_wallet()