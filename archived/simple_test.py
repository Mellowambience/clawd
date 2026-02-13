import tweepy
import json
from pathlib import Path

# Load credentials
config_file = Path('C:/Users/nator/clawd/x_api_config.json')
with open(config_file, 'r') as f:
    config = json.load(f)

x_config = config['x_api']

print("Current configuration:")
print(f"Consumer Key: {x_config['consumer_key'][:10]}...")
print(f"Consumer Secret: {x_config['consumer_secret'][:10]}...")
print(f"Access Token: {x_config['access_token'][:10]}...")
print(f"Access Token Secret: {x_config['access_token_secret'][:10]}...")

# Try creating a client with just the consumer credentials first
try:
    # Create a basic client
    client = tweepy.Client(
        consumer_key=x_config['consumer_key'],
        consumer_secret=x_config['consumer_secret'],
        access_token=x_config['access_token'],
        access_token_secret=x_config['access_token_secret']
    )
    
    print("\nClient created successfully. Attempting to get user info...")
    
    # Try to get user info
    me = client.get_me()
    print('Success! Account Information:')
    print(f'Username: @{me.data.username}')
    print(f'Display Name: {me.data.name}')
    
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
    print("\nThe credentials may still not be properly matched.")
    print("Make sure all four credentials belong to the same X Developer App.")