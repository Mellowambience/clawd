import tweepy
import json
from pathlib import Path

def test_x_api_connection():
    """Test X API connection with stored credentials"""
    
    # Load configuration
    config_file = Path(__file__).parent / "x_api_config.json"
    
    if not config_file.exists():
        print("Configuration file not found. Please run setup_x_api.py first.")
        return False
    
    with open(config_file, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            print("Invalid JSON in config file.")
            return False
    
    x_config = config.get('x_api', {})
    
    # Extract credentials
    access_token = x_config.get('access_token')
    access_token_secret = x_config.get('access_token_secret')
    consumer_key = x_config.get('consumer_key')
    consumer_secret = x_config.get('consumer_secret')
    
    # Check if all required credentials are present
    missing_creds = []
    if not access_token:
        missing_creds.append('access_token')
    if not access_token_secret:
        missing_creds.append('access_token_secret')
    if not consumer_key:
        missing_creds.append('consumer_key')
    if not consumer_secret:
        missing_creds.append('consumer_secret')
    
    if missing_creds:
        print(f"Missing required credentials: {', '.join(missing_creds)}")
        print("Please update your configuration using setup_x_api.py")
        return False
    
    try:
        # Initialize tweepy client
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Test the connection by fetching the authenticated user's info
        me = client.get_me()
        
        if me.data:
            print(f"✅ Successfully connected to X API!")
            print(f"👤 Connected as: @{me.data.username} ({me.data.name})")
            print(f"🆔 User ID: {me.data.id}")
            return True
        else:
            print("❌ Failed to retrieve user information")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to X API: {str(e)}")
        return False

if __name__ == "__main__":
    test_x_api_connection()