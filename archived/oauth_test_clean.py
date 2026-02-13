import tweepy
import json
from pathlib import Path

# Load credentials
config_file = Path('C:/Users/nator/clawd/x_api_config.json')
with open(config_file, 'r') as f:
    config = json.load(f)

x_config = config['x_api']

print("Testing individual credential authentication...")

# Test with OAuth 1a handler which is more explicit
try:
    auth = tweepy.OAuthHandler(
        x_config['consumer_key'],
        x_config['consumer_secret']
    )
    
    auth.set_access_token(
        x_config['access_token'],
        x_config['access_token_secret']
    )
    
    # Create API object using OAuth 1a
    api = tweepy.API(auth)
    
    # Verify credentials
    user = api.verify_credentials()
    
    print("[SUCCESS] Authentication successful!")
    print(f"Username: @{user.screen_name}")
    print(f"Display Name: {user.name}")
    print(f"Followers: {user.followers_count}")
    print(f"Following: {user.friends_count}")
    print(f"Tweets: {user.statuses_count}")
    
except tweepy.Unauthorized as e:
    print("[ERROR] Unauthorized: Could not authenticate you.")
    print("The access tokens do not match the consumer credentials.")
    print("You need to regenerate the access tokens using the same app as your consumer keys.")
except Exception as e:
    print(f"[ERROR] Error: {e}")