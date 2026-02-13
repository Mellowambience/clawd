#!/usr/bin/env python3
"""
Verification script for X API setup
"""

import json
from pathlib import Path

def verify_configuration():
    """Verify the X API configuration is complete"""
    config_file = Path(__file__).parent / "x_api_config.json"
    
    print("Verifying X API Configuration")
    print("=" * 30)
    
    if not config_file.exists():
        print("[ERROR] Configuration file not found!")
        return False
    
    with open(config_file, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON in config file!")
            return False
    
    x_config = config.get('x_api', {})
    
    # Check if all required fields are present
    access_token = x_config.get('access_token')
    access_token_secret = x_config.get('access_token_secret')
    consumer_key = x_config.get('consumer_key')
    consumer_secret = x_config.get('consumer_secret')
    
    print(f"Access Token: {'[SUCCESS] SET' if access_token and '1869555801792331776-hoHVzssNARduTcN9NZAjI6bGSAs2Vf' in access_token else '[ERROR] MISSING'}")
    print(f"Access Token Secret: {'[SUCCESS] SET' if access_token_secret and 'Xtd2kSIXaXXuj92mFdsg6DyJURAgIw5MKNdGCQr37jqS8' in access_token_secret else '[ERROR] MISSING'}")
    print(f"Consumer Key: {'[SUCCESS] SET' if consumer_key and consumer_key != 'YOUR_ACTUAL_API_KEY_HERE' else '[ERROR] PLACEHOLDER'}")
    print(f"Consumer Secret: {'[SUCCESS] SET' if consumer_secret and consumer_secret != 'YOUR_ACTUAL_API_SECRET_HERE' else '[ERROR] PLACEHOLDER'}")
    
    # Overall status
    all_set = (
        access_token and '1869555801792331776-hoHVzssNARduTcN9NZAjI6bGSAs2Vf' in access_token and
        access_token_secret and 'Xtd2kSIXaXXuj92mFdsg6DyJURAgIw5MKNdGCQr37jqS8' in access_token_secret and
        consumer_key and consumer_key != 'YOUR_ACTUAL_API_KEY_HERE' and
        consumer_secret and consumer_secret != 'YOUR_ACTUAL_API_SECRET_HERE'
    )
    
    if all_set:
        print("\n[SUCCESS] All required credentials are set!")
        print("Your X API setup is complete and ready to use.")
        return True
    else:
        print("\n[WARNING] Configuration is incomplete.")
        print("You need to update the consumer_key and consumer_secret with your actual API credentials.")
        print("\nTo complete the setup, edit the x_api_config.json file with your:")
        print("- Consumer Key (API Key)")
        print("- Consumer Secret (API Secret Key)")
        return False

if __name__ == "__main__":
    verify_configuration()