import tweepy
import json
from pathlib import Path

def check_account():
    """Check the X account information"""
    # Load credentials
    config_file = Path(__file__).parent / "x_api_config.json"
    with open(config_file, 'r') as f:
        config = json.load(f)

    x_config = config['x_api']

    # Create client
    try:
        client = tweepy.Client(
            consumer_key=x_config['consumer_key'],
            consumer_secret=x_config['consumer_secret'],
            access_token=x_config['access_token'],
            access_token_secret=x_config['access_token_secret']
        )

        # Try to get user info
        me = client.get_me()
        
        print('Account Information:')
        print(f'Username: @{me.data.username}')
        print(f'Display Name: {me.data.name}')
        print(f'User ID: {me.data.id}')
        print(f'Description: {me.data.description}')
        
        if hasattr(me.data, 'public_metrics'):
            followers_count = me.data.public_metrics['followers_count']
            following_count = me.data.public_metrics['following_count']
            tweets_count = me.data.public_metrics['tweet_count']
            print(f'Followers Count: {followers_count}')
            print(f'Following Count: {following_count}')
            print(f'Tweets Count: {tweets_count}')
        
        print(f'Account Created: {me.data.created_at}')
        
        return True
        
    except tweepy.Unauthorized as e:
        print(f"Authorization Error: {e}")
        print("This may indicate that the access tokens don't match the consumer credentials")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_account()