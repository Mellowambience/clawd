"""
Script to help regenerate X API tokens properly
This happens when access tokens don't match the consumer credentials
"""
import tweepy
import webbrowser
import json
from pathlib import Path

def regenerate_access_tokens():
    """
    Guide to regenerate access tokens that match your consumer credentials
    """
    print("Regenerating X API Access Tokens")
    print("=" * 40)
    print()
    
    # Load current config
    config_file = Path(__file__).parent / "x_api_config.json"
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    consumer_key = config['x_api']['consumer_key']
    consumer_secret = config['x_api']['consumer_secret']
    
    print("To fix the authorization error, you need to regenerate your access tokens")
    print("using the same app that corresponds to your consumer key and secret.\n")
    
    print("Steps to regenerate access tokens:")
    print("1. Go to https://developer.twitter.com/en/portal/projects-and-apps")
    print("2. Find the app that corresponds to consumer key:", consumer_key[:10], "...")
    print("3. Click on 'Keys and tokens' for that app")
    print("4. Under 'Access token and secret', click 'Regenerate'")
    print("5. Copy the new access token and secret")
    print("6. Update your config file with the new tokens\n")
    
    print("Alternatively, you can generate new tokens with OAuth flow:")
    print("(This requires manual steps)")
    print()
    
    print("If you want to try the OAuth 1a flow to get new tokens, you would need to:")
    print("1. Install tweepy with: pip install tweepy")
    print("2. Run this code with your consumer credentials:")
    print()
    print("# OAuth 1a flow")
    print("auth = tweepy.OAuthHandler(consumer_key, consumer_secret)")
    print("redirect_url = auth.get_authorization_url()")
    print("print('Visit this URL to authorize:', redirect_url)")
    print("# Then visit the URL, authorize the app, and copy the PIN")
    print("# Finally:")
    print("# auth.get_access_token(verifier=pin_from_user)")
    print("# print('Access Token:', auth.access_token)")
    print("# print('Access Token Secret:', auth.access_token_secret)")
    
    print("\nAfter regenerating the tokens, update your x_api_config.json file.")
    print("Make sure all four credentials belong to the same X Developer App.")

if __name__ == "__main__":
    regenerate_access_tokens()