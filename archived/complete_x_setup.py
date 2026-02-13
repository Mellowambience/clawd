#!/usr/bin/env python3
"""
Complete X API setup script
This script will help you configure your X API credentials properly
"""

import json
import os
from pathlib import Path

def complete_x_api_setup():
    """Complete the X API setup process"""
    
    print("Complete X API Setup")
    print("=" * 30)
    print()
    
    # Get the directory of this script
    config_dir = Path(__file__).parent
    config_file = config_dir / "x_api_config.json"
    
    print("I see you have access tokens, but we need to complete the configuration")
    print("with your consumer key and secret to enable full X API access.\n")
    
    print("To get your consumer key and secret:")
    print("1. Go to https://developer.twitter.com/en/apply-for-access")
    print("2. Apply for a developer account if you haven't already")
    print("3. Create a new app in your developer portal")
    print("4. Once approved, you'll find your Consumer Key and Secret in the app settings\n")
    
    # Load existing config
    if config_file.exists():
        with open(config_file, 'r') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                print("Invalid JSON in config file. Using defaults.")
                config = {"x_api": {}}
    else:
        config = {"x_api": {}}
    
    x_config = config.get('x_api', {})
    
    print("Current configuration:")
    print(f"- Access Token: {'SET' if x_config.get('access_token') else 'NOT SET'}")
    print(f"- Access Token Secret: {'SET' if x_config.get('access_token_secret') else 'NOT SET'}")
    print(f"- Consumer Key: {'SET' if x_config.get('consumer_key') and 'YOUR_' not in x_config.get('consumer_key', '') else 'NEEDS SETTING'}")
    print(f"- Consumer Secret: {'SET' if x_config.get('consumer_secret') and 'YOUR_' not in x_config.get('consumer_secret', '') else 'NEEDS SETTING'}")
    print()
    
    # If consumer keys are still placeholder values, ask for them
    if 'YOUR_CONSUMER_KEY_HERE' in x_config.get('consumer_key', ''):
        print("Please enter your Consumer Key from the X Developer Portal:")
        consumer_key = input("Consumer Key: ").strip()
        if consumer_key:
            x_config['consumer_key'] = consumer_key
            print("Consumer Key updated.\n")
    
    if 'YOUR_CONSUMER_SECRET_HERE' in x_config.get('consumer_secret', ''):
        print("Please enter your Consumer Secret from the X Developer Portal:")
        consumer_secret = input("Consumer Secret: ").strip()
        if consumer_secret:
            x_config['consumer_secret'] = consumer_secret
            print("Consumer Secret updated.\n")
    
    # Confirm all values are set
    missing_values = []
    if not x_config.get('access_token') or '1869555801792331776-hoHVzssNARduTcN9NZAjI6bGSAs2Vf' not in x_config.get('access_token', ''):
        missing_values.append('Access Token')
    if not x_config.get('access_token_secret') or 'Xtd2kSIXaXXuj92mFdsg6DyJURAgIw5MKNdGCQr37jqS8' not in x_config.get('access_token_secret', ''):
        missing_values.append('Access Token Secret')
    if not x_config.get('consumer_key') or 'YOUR_' in x_config.get('consumer_key', ''):
        missing_values.append('Consumer Key')
    if not x_config.get('consumer_secret') or 'YOUR_' in x_config.get('consumer_secret', ''):
        missing_values.append('Consumer Secret')
    
    if missing_values:
        print(f"Still missing: {', '.join(missing_values)}")
        print("\nYou'll need to obtain these from the X Developer Portal:")
        print("https://developer.twitter.com/")
        return False
    
    # Update the config
    config['x_api'] = x_config
    
    # Save the updated configuration
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set secure file permissions
    os.chmod(config_file, 0o600)
    
    print("✅ Configuration completed successfully!")
    print(f"Config file saved: {config_file}")
    print("\nThe file has been secured with read/write permissions for owner only.")
    
    # Offer to test the connection
    test = input("\nWould you like to test the connection now? (y/n): ")
    if test.lower() == 'y':
        try:
            import tweepy
            # Initialize tweepy client
            client = tweepy.Client(
                consumer_key=x_config['consumer_key'],
                consumer_secret=x_config['consumer_secret'],
                access_token=x_config['access_token'],
                access_token_secret=x_config['access_token_secret']
            )
            
            # Test the connection
            me = client.get_me()
            
            if me.data:
                print(f"\n🎉 Success! Connected to X API as @{me.data.username}")
                print("Your X API setup is complete and working!")
                return True
            else:
                print("\n❌ Could not retrieve user information")
                return False
                
        except Exception as e:
            print(f"\n❌ Error testing connection: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    complete_x_api_setup()