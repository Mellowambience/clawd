#!/usr/bin/env python3
"""
Script to manage both agents - the original wallet and the new working one
"""

import json
from pathlib import Path

def update_config_for_both_agents():
    # Load current config
    config_dir = Path.home() / ".clawtasks"
    config_file = config_dir / "config.json"
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print("Current config:")
    print(json.dumps(config, indent=2))
    
    # The original wallet that's registered but not showing in public list
    original_wallet = "0x212d3a3D4a78EA78c54d54f37a9bE9e5e020Bf75"
    
    # The new working agent we created
    new_agent_config = {
        "api_key": config["api_key"],  # This is the API key for the new agent
        "wallet_address": config["wallet_address"],
        "agent_name": config["agent_name"],
        "created_at": config["created_at"]
    }
    
    # We need to find the API key for the original wallet somehow
    # Since we can't find it in the public list, we'll store both configurations
    # The original wallet might need account recovery
    
    print(f"\nOriginal wallet: {original_wallet}")
    print(f"New working agent: {new_agent_config['agent_name']} with wallet {new_agent_config['wallet_address']}")
    
    # Update the config to include info about both
    enhanced_config = {
        "current_active_agent": new_agent_config,  # This one is working now
        "original_wallet": original_wallet,  # This one is registered but inaccessible
        "new_working_agent": new_agent_config,
        "notes": "Original wallet registered but API key unknown. New agent created and operational."
    }
    
    # Save enhanced config
    with open(config_file, 'w') as f:
        json.dump(enhanced_config, f, indent=2)
    
    print(f"\nEnhanced config saved:")
    print(json.dumps(enhanced_config, indent=2))
    
    # Update .env file to reflect current working agent
    env_file = Path.cwd() / ".env"
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    # Find and update the CLAWTASKS entries
    lines = env_content.split('\n')
    updated_lines = []
    updated_api_key = False
    updated_wallet = False
    updated_agent_name = False
    
    for line in lines:
        if line.startswith('CLAWTASKS_API_KEY='):
            updated_lines.append(f'CLAWTASKS_API_KEY={new_agent_config["api_key"]}')
            updated_api_key = True
        elif line.startswith('CLAWTASKS_WALLET='):
            updated_lines.append(f'CLAWTASKS_WALLET={new_agent_config["wallet_address"]}')
            updated_wallet = True
        elif line.startswith('CLAWTASKS_AGENT_NAME='):
            updated_lines.append(f'CLAWTASKS_AGENT_NAME={new_agent_config["agent_name"]}')
            updated_agent_name = True
        else:
            updated_lines.append(line)
    
    # Add missing entries if needed
    if not updated_api_key:
        updated_lines.append(f'CLAWTASKS_API_KEY={new_agent_config["api_key"]}')
    if not updated_wallet:
        updated_lines.append(f'CLAWTASKS_WALLET={new_agent_config["wallet_address"]}')
    if not updated_agent_name:
        updated_lines.append(f'CLAWTASKS_AGENT_NAME={new_agent_config["agent_name"]}')
    
    # Add original wallet info
    updated_lines.append(f'# Original wallet (registered but API key unknown)')
    updated_lines.append(f'CLAWTASKS_ORIGINAL_WALLET={original_wallet}')
    
    with open(env_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"\n.env file updated with current working agent and original wallet info")
    
    print(f"\nSUMMARY:")
    print(f"- Current working agent: {new_agent_config['agent_name']} (earning bounties)")
    print(f"- Current working wallet: {new_agent_config['wallet_address']}")
    print(f"- Original wallet: {original_wallet} (registered but API key unknown)")
    print(f"- To recover original agent: Need to contact ClawTasks support or find recovery method")

if __name__ == "__main__":
    update_config_for_both_agents()