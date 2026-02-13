#!/usr/bin/env python3
"""
Complete Setup Script for X Platform Integration
Configures the MIST system with all X API credentials
"""

import asyncio
from x_integration.X_INTEGRATION import XIntegration
from integration.CORE_HUB import CoreHub


async def setup_full_x_integration(api_key: str, api_secret: str, access_token: str, 
                                  access_token_secret: str, bearer_token: str):
    """
    Complete setup of X integration with all required credentials
    """
    print("Completing X Platform Integration Setup for MIST...")
    print("=" * 50)
    
    # Initialize core hub temporarily for the setup
    hub = CoreHub()
    await hub.start()
    
    # Create X integration instance
    x_integration = XIntegration(hub)
    
    # Set up the connection using the credentials
    await x_integration.setup_x_connection(
        api_key, api_secret, access_token, access_token_secret, bearer_token
    )
    
    # Verify the connection by checking if the API client was created
    if x_integration.x_api_handler.client is not None:
        print("✅ X Platform Integration configured successfully!")
        
        # Update configuration to enable functionality
        config = x_integration.config_manager.load_config()
        config['enabled'] = True
        config['auto_post_mist_insights'] = False  # Start conservative
        config['auto_post_ai_agents'] = False      # Start conservative
        x_integration.config_manager.save_config(config)
        
        # Update the handler configuration
        x_integration.x_api_handler.config.enabled = True
        x_integration.x_api_handler.config.auto_post_mist_insights = False
        x_integration.x_api_handler.config.auto_post_ai_agents = False
        
        print("\n📋 Current Configuration:")
        print(f"   - Enabled: {config['enabled']}")
        print(f"   - Auto-post MIST insights: {config['auto_post_mist_insights']}")
        print(f"   - Auto-post AI agents: {config['auto_post_ai_agents']}")
        print(f"   - Content filtering: {config['content_filter_enabled']}")
        
        # Show privacy settings
        print("\n🔒 Privacy Controls Active:")
        for category, allowed in config['privacy_controls'].items():
            status = "✅" if allowed else "❌"
            print(f"   {status} {category}: {'Allowed' if allowed else 'Blocked'}")
        
        print("\n💡 Tips:")
        print("   - Auto-posting is disabled by default for privacy")
        print("   - Content is filtered based on privacy settings")
        print("   - You can enable specific content types through configuration")
        
    else:
        print("❌ Failed to establish X Platform connection")
        print("   Please verify all credentials are correct")
    
    # Shutdown hub
    await hub.shutdown()
    
    print("\n" + "=" * 50)
    print("Setup process completed!")
    return x_integration.x_api_handler.client is not None


def main():
    """
    Main setup function with sample credentials
    NOTE: Replace the empty strings with actual tokens
    """
    print("X Platform Integration - Complete Setup")
    print("=" * 50)
    print("Please note: This setup requires ALL five X API credentials.")
    print("")
    
    # Sample placeholders - replace with actual credentials
    api_key = "Hsi56Z3ATMI4kaJN3hPAMT3ZB"
    api_secret = "9oFQ8dDeiWfaHN9nR7kVazEyVMTqTkSRySMXWsBn0YSH4iBABN"
    
    # These need to be provided by the user
    access_token = input("Enter your Access Token: ").strip()
    access_token_secret = input("Enter your Access Token Secret: ").strip()
    bearer_token = input("Enter your Bearer Token: ").strip()
    
    if not all([access_token, access_token_secret, bearer_token]):
        print("\n❌ All credentials are required for X integration setup!")
        print("Please obtain the missing credentials from the X Developer Portal.")
        return False
    
    print(f"\nSetting up X integration...")
    print("⚠️  Your credentials will be stored securely and encrypted.")
    
    response = input("Continue with setup? (y/n): ").lower().strip()
    if response not in ['y', 'yes']:
        print("Setup cancelled.")
        return False
    
    # Run the async setup
    success = asyncio.run(setup_full_x_integration(
        api_key, api_secret, access_token, access_token_secret, bearer_token
    ))
    
    if success:
        print("\n🎉 X Platform Integration is now configured and ready!")
        print("You can start the main MIST Hub with: python LAUNCH_MIST_HUB.py")
    else:
        print("\n💥 Setup failed. Please check your credentials and try again.")


if __name__ == "__main__":
    main()