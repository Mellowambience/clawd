"""
Final X API verification script without problematic unicode characters
"""

import tweepy
import json


def simple_verify_x_access():
    """Simple verification of X API access without problematic characters"""
    try:
        # Load config
        with open('x_api_config.json', 'r') as f:
            config = json.load(f)
        
        x_config = config['x_api']
        
        # Create tweepy client
        client = tweepy.Client(
            bearer_token=x_config.get('bearer_token'),
            consumer_key=x_config['consumer_key'],
            consumer_secret=x_config['consumer_secret'],
            access_token=x_config['access_token'],
            access_token_secret=x_config['access_token_secret']
        )
        
        print("Verifying X API access...")
        
        # Test read access
        try:
            me = client.get_me()
            print(f"SUCCESS: Authenticated as @{me.data.username}")
            print(f"Account verified: {me.data.name}")
        except Exception as e:
            print(f"FAILED: Authentication error - {e}")
            return False
        
        # Test write access
        try:
            test_tweet = client.create_tweet(
                text="Testing write permissions for Clawdbot Hub"
            )
            tweet_id = test_tweet.data['id']
            print(f"SUCCESS: Write access confirmed - Tweet ID: {tweet_id}")
            
            # Clean up test tweet
            client.delete_tweet(tweet_id)
            print("SUCCESS: Test tweet cleaned up")
            
        except tweepy.Unauthorized as e:
            print(f"FAILED: Authentication issue - {e}")
            return False
        except tweepy.Forbidden as e:
            print(f"FAILED: Insufficient permissions - {e}")
            print("\nSOLUTION REQUIRED:")
            print("Go to X Developer Portal -> App Settings -> Permissions")
            print("Change from 'Read' to 'Read and Write' permissions")
            return False
        except Exception as e:
            print(f"FAILED: Write test error - {e}")
            return False
        
        print("\nSUCCESS: X API is fully configured for Clawdbot Hub integration!")
        print("The content pipeline can now post to X automatically.")
        return True
        
    except Exception as e:
        print(f"Configuration error: {e}")
        return False


if __name__ == "__main__":
    simple_verify_x_access()