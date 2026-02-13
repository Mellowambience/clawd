#!/usr/bin/env python3
"""
Setup Script for X Platform Integration
Configures the MIST system with X API credentials
"""

import asyncio
from x_integration.X_CONFIG_MANAGER import XConfigManager
from x_integration.X_INTEGRATION import XIntegration
from integration.CORE_HUB import CoreHub


async def setup_x_integration(api_key: str, api_secret: str, access_token: str, 
                             access_token_secret: str, bearer_token: str):
    """
    Setup X integration with provided credentials
    """
    print("Setting up X Platform Integration for MIST...")
    
    # Initialize core hub temporarily for the setup
    hub = CoreHub()
    await hub.start()
    
    # Create config manager and save credentials securely
    config_manager = XConfigManager()
    
    print("Saving X credentials securely...")
    success = config_manager.save_credentials(
        api_key, api_secret, access_token, access_token_secret, bearer_token
    )
    
    if not success:
        print("Failed to save X credentials securely")
        await hub.shutdown()
        return False
    
    # Create X integration instance
    x_integration = XIntegration(hub)
    
    # Enable X integration in config
    config = config_manager.load_config()
    config['enabled'] = True
    config['auto_post_mist_insights'] = False  # Default to manual approval
    config['auto_post_ai_agents'] = False      # Default to manual approval
    config_manager.save_config(config)
    
    print("X Platform Integration configured successfully!")
    print("Current settings:")
    print(f"- Enabled: {config['enabled']}")
    print(f"- Auto-post MIST insights: {config['auto_post_mist_insights']}")
    print(f"- Auto-post AI agents: {config['auto_post_ai_agents']}")
    print(f"- Content filtering: {config['content_filter_enabled']}")
    
    # Shutdown hub
    await hub.shutdown()
    
    print("\nSetup complete! The X integration is now configured.")
    print("To enable automatic posting, update the configuration through the main hub.")
    return True


def main():
    """
    Main setup function
    """
    # X API credentials provided by the user
    api_key = "Hsi56Z3ATMI4kaJN3hPAMT3ZB"
    api_secret = "9oFQ8dDeiWfaHN9nR7kVazEyVMTqTkSRySMXWsBn0YSH4iBABN"
    access_token = ""  # Need to be provided
    access_token_secret = ""  # Need to be provided
    bearer_token = ""  # Need to be provided
    
    print("X Platform Integration Setup")
    print("=" * 40)
    print("Note: The full X integration requires all API credentials.")
    print("You provided the API key and secret, but we also need:")
    print("- Access Token")
    print("- Access Token Secret") 
    print("- Bearer Token")
    print("")
    
    # For now, we'll just store the provided credentials
    # In a real scenario, we would need all tokens
    print("Would you like to proceed with partial setup?")
    print("This will store the provided credentials but X integration will remain disabled until complete.")
    
    response = input("Proceed? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        # Since we don't have all required credentials, we'll just create the config
        config_manager = XConfigManager()
        
        print("Storing partial credentials...")
        # We'll store what we have, but mark as incomplete
        import json
        from pathlib import Path
        
        config_dir = Path("./config")
        config_dir.mkdir(exist_ok=True)
        
        # Create a partial config indicating incomplete setup
        partial_config = {
            "api_key_provided": bool(api_key),
            "api_secret_provided": bool(api_secret),
            "setup_completed": False,
            "instructions": "Complete setup requires: access_token, access_token_secret, and bearer_token"
        }
        
        with open(config_dir / "x_partial_config.json", 'w') as f:
            json.dump(partial_config, f, indent=2)
        
        print("Partial setup recorded. Complete credentials needed for full functionality.")


if __name__ == "__main__":
    main()