"""
Setup for X API using Bearer Token authentication
This bypasses the need for matching access tokens and consumer credentials
"""
import json
import tweepy
from pathlib import Path

def setup_bearer_auth():
    """Setup X API access using Bearer Token (application-only auth)"""
    
    print("Setting up X API with Bearer Token Authentication")
    print("=" * 50)
    print()
    
    # Load existing config
    config_file = Path(__file__).parent / "x_api_config.json"
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    x_config = config['x_api']
    
    print("To use Bearer Token authentication, you need to get a Bearer Token")
    print("from your X Developer App settings. Here's how:")
    print()
    print("1. Go to https://developer.twitter.com/en/portal/projects-and-apps")
    print("2. Select your app")
    print("3. Go to the 'Keys and tokens' tab")
    print("4. Under 'Authentication Tokens', find your Bearer Token")
    print("5. If you don't see it, click 'Regenerate' under Bearer Token")
    print()
    
    # Ask for Bearer Token
    bearer_token = input("Enter your Bearer Token (or press Enter to skip): ").strip()
    
    if bearer_token:
        # Update config with Bearer Token
        config['x_api']['bearer_token'] = bearer_token
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Bearer Token added to configuration!")
        
        # Test the Bearer Token
        try:
            # Create client with Bearer Token only
            client = tweepy.Client(bearer_token=bearer_token)
            
            # Test by getting user info
            me = client.get_me()
            print(f"[SUCCESS] Authenticated as: @{me.data.username}")
            print("Bearer token authentication is working!")
            
        except Exception as e:
            print(f"[ERROR] Could not authenticate with Bearer Token: {e}")
            print("Please verify your Bearer Token is correct.")
    
    else:
        print("Skipping Bearer Token setup.")
        print()
        print("Alternative solution:")
        print("If you have your API Key and Secret (Consumer Key/Secret),")
        print("we can try to programmatically obtain a Bearer Token:")
        print()
        
        # Try to get Bearer Token programmatically using consumer credentials
        try:
            import requests
            import base64
            
            # Prepare credentials for OAuth2 token request
            consumer_key = x_config['consumer_key']
            consumer_secret = x_config['consumer_secret']
            
            # Create the bearer token by making a request to the OAuth2 token endpoint
            key_secret = f"{consumer_key}:{consumer_secret}"
            encoded_key = base64.b64encode(key_secret.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            response = requests.post('https://api.twitter.com/oauth2/token', headers=headers, data=data)
            
            if response.status_code == 200:
                bearer_token = response.json()['access_token']
                print(f"Successfully obtained Bearer Token: {bearer_token[:20]}...")
                
                # Update config
                config['x_api']['bearer_token'] = bearer_token
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                # Test the token
                client = tweepy.Client(bearer_token=bearer_token)
                # Test with a simple API call that doesn't require user context
                trends = client.get_place_trends(id=1)  # Global trends
                print("[SUCCESS] Bearer token authentication is working!")
                print("You can now use the X API with application-only authentication.")
                
            else:
                print(f"Failed to obtain Bearer Token. Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            print(f"Could not obtain Bearer Token programmatically: {e}")
            print()
            print("The most reliable solution is still to ensure your access tokens")
            print("match your consumer credentials in the X Developer Portal.")

if __name__ == "__main__":
    setup_bearer_auth()