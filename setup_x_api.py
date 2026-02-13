import json
import os
from pathlib import Path

def setup_x_api_config():
    """Setup X API configuration with proper error handling"""
    
    print("X API Configuration Setup")
    print("=" * 30)
    
    # Get the directory of this script
    config_dir = Path(__file__).parent
    config_file = config_dir / "x_api_config.json"
    
    # Check if config file exists
    if config_file.exists():
        with open(config_file, 'r') as f:
            try:
                config = json.load(f)
                print("Existing configuration found:")
                print("- Access token: {}".format(config.get('x_api', {}).get('access_token', '')[:20] + "..." if config.get('x_api', {}).get('access_token') else "Not set"))
                print("- Consumer key: {}".format(config.get('x_api', {}).get('consumer_key', '')[:20] + "..." if config.get('x_api', {}).get('consumer_key') else "Not set"))
                
                update = input("\nWould you like to update the configuration? (y/n): ")
                if update.lower() != 'y':
                    print("Configuration unchanged.")
                    return
            except json.JSONDecodeError:
                print("Invalid JSON in config file. Will recreate.")
                config = {"x_api": {}}
    else:
        config = {"x_api": {}}
    
    # Collect API credentials
    print("\nEnter your X API credentials:")
    print("(Leave blank to keep existing values)")
    
    # Access Token
    current_access_token = config['x_api'].get('access_token', '')
    new_access_token = input(f"Access Token [{current_access_token[:20]}...]: ").strip()
    if new_access_token:
        config['x_api']['access_token'] = new_access_token
    elif not current_access_token:
        config['x_api']['access_token'] = input("Access Token (required): ").strip()
    
    # Access Token Secret
    current_access_secret = config['x_api'].get('access_token_secret', '')
    new_access_secret = input(f"Access Token Secret [{current_access_secret[:20]}...]: ").strip()
    if new_access_secret:
        config['x_api']['access_token_secret'] = new_access_secret
    elif not current_access_secret:
        config['x_api']['access_token_secret'] = input("Access Token Secret (required): ").strip()
    
    # Consumer Key
    current_consumer_key = config['x_api'].get('consumer_key', '')
    new_consumer_key = input(f"Consumer Key [{current_consumer_key[:20]}...]: ").strip()
    if new_consumer_key:
        config['x_api']['consumer_key'] = new_consumer_key
    elif not current_consumer_key:
        config['x_api']['consumer_key'] = input("Consumer Key (required): ").strip()
    
    # Consumer Secret
    current_consumer_secret = config['x_api'].get('consumer_secret', '')
    new_consumer_secret = input(f"Consumer Secret [{current_consumer_secret[:20]}...]: ").strip()
    if new_consumer_secret:
        config['x_api']['consumer_secret'] = new_consumer_secret
    elif not current_consumer_secret:
        config['x_api']['consumer_secret'] = input("Consumer Secret (required): ").strip()
    
    # Save configuration
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nConfiguration saved to {config_file}")
    print("\nTo use these credentials in Python applications, you can load them like this:")
    print("""
import json
with open('x_api_config.json', 'r') as f:
    config = json.load(f)
    
access_token = config['x_api']['access_token']
access_token_secret = config['x_api']['access_token_secret']
consumer_key = config['x_api']['consumer_key']
consumer_secret = config['x_api']['consumer_secret']
""")
    
    # Set appropriate file permissions for security
    os.chmod(config_file, 0o600)  # Read/write for owner only
    print("\nFile permissions set to read/write for owner only for security.")

if __name__ == "__main__":
    setup_x_api_config()