#!/usr/bin/env python3
"""
Setup script for ClawTasks bounty hunter
Handles registration and configuration
"""

import requests
import json
import os
from pathlib import Path

REQUEST_TIMEOUT = 10

def register_agent(agent_name: str, wallet_address: str = None):
    """Register a new agent on ClawTasks"""
    url = "https://clawtasks.com/api/agents"
    
    payload = {"name": agent_name}
    if wallet_address:
        payload["wallet_address"] = wallet_address
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Registering agent: {agent_name}")
    if wallet_address:
        print(f"Using wallet: {wallet_address}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            print("Registration successful!")
            print(json.dumps(result, indent=2))
            
            # Save the API key and other details to a config file
            save_config(result)
            return result
        else:
            print(f"Registration failed with status {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error during registration: {e}")
        return None

def save_config(registration_result: dict):
    """Save configuration to a local file"""
    config = {
        "api_key": registration_result.get("api_key"),
        "wallet_address": registration_result.get("wallet", {}).get("address"),
        "agent_name": registration_result.get("name"),
        "verification_code": registration_result.get("verification_code"),
        "created_at": registration_result.get("created_at")
    }
    
    # Create config directory if it doesn't exist
    config_dir = Path.home() / ".clawtasks"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to {config_file}")
    
    # Also create a .env file for easy loading
    env_file = Path.cwd() / ".env"
    with open(env_file, 'a') as f:  # Append to existing .env
        f.write(f"\n# ClawTasks Configuration\n")
        f.write(f"CLAWTASKS_API_KEY={config['api_key']}\n")
        f.write(f"CLAWTASKS_WALLET={config['wallet_address']}\n")
        f.write(f"CLAWTASKS_AGENT_NAME={config['agent_name']}\n")
    
    print(f"Environment variables added to {env_file}")

def load_config():
    """Load configuration from file"""
    config_dir = Path.home() / ".clawtasks"
    config_file = config_dir / "config.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return None

def verify_agent(api_key: str):
    """Verify the agent after registration"""
    url = "https://clawtasks.com/api/agents/verify"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            print("Verification successful!")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"Verification failed with status {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error during verification: {e}")
        return None

def main():
    print("ClawTasks Bounty Hunter Setup")
    print("=" * 40)
    
    # Get agent name from user
    agent_name = input("Enter your agent name (e.g., MistBountyHunter): ").strip()
    if not agent_name:
        agent_name = "MistBountyHunter"
    
    # Get wallet address from user (optional)
    wallet_address = input("Enter your Base wallet address (optional, press Enter to skip): ").strip()
    if not wallet_address:
        wallet_address = None
    
    # Attempt registration
    result = register_agent(agent_name, wallet_address)
    
    if result:
        print("\nNext steps:")
        print("1. Check your verification code in the output above")
        print("2. Post the verification code on Moltbook as instructed in the response")
        print("3. Run the verification step once you've posted on Moltbook")
        
        # Optionally verify now
        verify_now = input("\nWould you like to verify now? (y/n): ").strip().lower()
        if verify_now == 'y':
            api_key = result.get("api_key")
            if api_key:
                verify_agent(api_key)
            else:
                print("No API key found in registration result")
    else:
        print("\nRegistration failed. The API might be temporarily down.")
        print("Try again later, or check https://clawtasks.com for service status.")

if __name__ == "__main__":
    main()
