"""
Automatically generate a Bearer Token using consumer credentials
"""
import requests
import base64
import json
from pathlib import Path

def generate_bearer_token():
    """Generate a Bearer Token using consumer credentials"""
    
    # Load existing config
    config_file = Path(__file__).parent / "x_api_config.json"
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    x_config = config['x_api']
    
    print("Generating Bearer Token using consumer credentials...")
    
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
    
    try:
        response = requests.post('https://api.twitter.com/oauth2/token', headers=headers, data=data)
        
        if response.status_code == 200:
            bearer_token = response.json()['access_token']
            print(f"Successfully obtained Bearer Token: {bearer_token[:20]}...")
            
            # Update config
            config['x_api']['bearer_token'] = bearer_token
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Bearer Token added to configuration!")
            print()
            print("Bearer token authentication is now set up.")
            print("You can use this for application-only API requests.")
            print("Note: This will allow reading public data but not user-specific actions.")
            return True
            
        else:
            print(f"❌ Failed to obtain Bearer Token. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error obtaining Bearer Token: {e}")
        return False

if __name__ == "__main__":
    generate_bearer_token()