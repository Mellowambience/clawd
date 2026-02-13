"""
Verify X API permissions and provide guidance for fixing permission issues
"""

import tweepy
import json


def verify_x_permissions():
    """Verify X API permissions"""
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
        
        print("Testing X API permissions...")
        
        # Test read permissions (should work with read-only)
        try:
            me = client.get_me()
            print(f"[OK] Read permissions: OK - Authenticated as @{me.data.username}")
        except Exception as e:
            print(f"[ERROR] Read permissions: FAILED - {e}")
            return False
        
        # Test write permissions (requires read+write)
        try:
            # Try to post a test tweet
            response = client.create_tweet(text="Test tweet to verify write permissions")
            print(f"[OK] Write permissions: OK - Test tweet created with ID: {response.data['id']}")
            
            # Clean up the test tweet
            client.delete_tweet(response.data['id'])
            print("[OK] Test tweet cleaned up successfully")
        except Exception as e:
            print(f"[ERROR] Write permissions: FAILED - {e}")
            print("\nRECOMMENDATION:")
            print("1. Go to your X Developer Portal: https://developer.twitter.com/")
            print("2. Select your app")
            print("3. Go to 'App Settings' or 'Permissions'")
            print("4. Change the permission from 'Read' to 'Read and Write'")
            print("5. Regenerate your access tokens if required")
            print("6. Update x_api_config.json with new credentials if needed")
            return False
        
        print("\n[SUCCESS] All X API permissions verified successfully!")
        return True
        
    except Exception as e:
        print(f"Error verifying X API permissions: {e}")
        return False


if __name__ == "__main__":
    verify_x_permissions()