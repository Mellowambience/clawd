#!/usr/bin/env python3
"""
Create a placeholder configuration for testing
"""

import json
from pathlib import Path

def create_placeholder_config():
    # Create the config directory if it doesn't exist
    config_dir = Path.home() / ".clawtasks"
    config_dir.mkdir(exist_ok=True)
    
    # Create a placeholder config
    config = {
        "api_key": "PLACEHOLDER_API_KEY_FOR_TESTING",
        "wallet_address": "0x212d3a3D4a78EA78c54d54f37a9bE9e5e020Bf75",
        "agent_name": "mist_bh_01",
        "created_at": "2026-02-01T12:00:00Z"
    }
    
    config_file = config_dir / "config.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Placeholder configuration created at {config_file}")
    print("This allows the system to run in test mode")
    
    # Also add to .env file
    env_file = Path.cwd() / ".env"
    with open(env_file, 'a') as f:
        f.write(f"\n# ClawTasks Configuration (PLACEHOLDER FOR TESTING)\n")
        f.write(f"CLAWTASKS_API_KEY=PLACEHOLDER_API_KEY_FOR_TESTING\n")
        f.write(f"CLAWTASKS_WALLET=0x212d3a3D4a78EA78c54d54f37a9bE9e5e020Bf75\n")
        f.write(f"CLAWTASKS_AGENT_NAME=mist_bh_01\n")
    
    print(f"Environment variables added to {env_file}")

if __name__ == "__main__":
    create_placeholder_config()