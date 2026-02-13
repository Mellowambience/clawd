#!/usr/bin/env python3
"""
X API Helper Script
Use this script to interact with the X API once you have all required credentials
"""

import json
import tweepy
from pathlib import Path

def load_x_credentials():
    """Load X API credentials from config file"""
    config_file = Path(__file__).parent / "x_api_config.json"
    
    if not config_file.exists():
        print("Configuration file not found!")
        print("Please ensure x_api_config.json exists with all required credentials.")
        return None
    
    with open(config_file, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            print("Invalid JSON in config file!")
            return None
    
    x_config = config.get('x_api', {})
    
    # Check if all required credentials are present
    required_fields = ['access_token', 'access_token_secret', 'consumer_key', 'consumer_secret']
    missing_fields = [field for field in required_fields 
                      if not x_config.get(field) or 'YOUR_' in str(x_config.get(field, ''))]
    
    if missing_fields:
        print(f"Missing required credentials: {', '.join(missing_fields)}")
        print("\nTo complete your X API setup:")
        print("1. Go to https://developer.twitter.com/")
        print("2. Create a developer account if you don't have one")
        print("3. Create a new app in your developer portal")
        print("4. Obtain your Consumer Key and Consumer Secret")
        print("5. Add these to your x_api_config.json file")
        return None
    
    return x_config

def create_x_client():
    """Create a tweepy client with loaded credentials"""
    creds = load_x_credentials()
    if not creds:
        return None
    
    try:
        client = tweepy.Client(
            consumer_key=creds['consumer_key'],
            consumer_secret=creds['consumer_secret'],
            access_token=creds['access_token'],
            access_token_secret=creds['access_token_secret']
        )
        return client
    except Exception as e:
        print(f"Error creating X API client: {e}")
        return None

def post_tweet(text):
    """Post a tweet using the X API"""
    client = create_x_client()
    if not client:
        return False
    
    try:
        response = client.create_tweet(text=text)
        if response.data:
            print(f"Tweet posted successfully! Tweet ID: {response.data['id']}")
            return True
        else:
            print("Failed to post tweet.")
            return False
    except Exception as e:
        print(f"Error posting tweet: {e}")
        return False

def get_my_tweets(count=10):
    """Get your recent tweets"""
    client = create_x_client()
    if not client:
        return []
    
    try:
        # Get the authenticated user's ID first
        me = client.get_me()
        if not me.data:
            print("Could not retrieve user information")
            return []
        
        # Get user's tweets
        tweets = client.get_users_tweets(
            id=me.data.id,
            max_results=count,
            tweet_fields=['created_at', 'public_metrics']
        )
        
        if tweets.data:
            print(f"Recent tweets from @{me.data.username}:")
            for i, tweet in enumerate(tweets.data, 1):
                print(f"{i}. {tweet.text[:100]}{'...' if len(tweet.text) > 100 else ''}")
                print(f"   ID: {tweet.id}, Created: {tweet.created_at}")
                print()
        else:
            print("No tweets found.")
        
        return tweets.data
    except Exception as e:
        print(f"Error retrieving tweets: {e}")
        return []

def search_tweets(query, count=10):
    """Search for tweets containing a specific query"""
    client = create_x_client()
    if not client:
        return []
    
    try:
        tweets = client.search_recent_tweets(
            query=query,
            max_results=count,
            tweet_fields=['author_id', 'created_at', 'public_metrics']
        )
        
        if tweets.data:
            print(f"Tweets containing '{query}':")
            for i, tweet in enumerate(tweets.data, 1):
                print(f"{i}. {tweet.text[:100]}{'...' if len(tweet.text) > 100 else ''}")
                print(f"   Author: {tweet.author_id}, Created: {tweet.created_at}")
                print()
        else:
            print(f"No tweets found for query '{query}'.")
        
        return tweets.data
    except Exception as e:
        print(f"Error searching tweets: {e}")
        return []

if __name__ == "__main__":
    print("X API Helper")
    print("=" * 30)
    print("Available functions:")
    print("1. Load credentials")
    print("2. Test connection")
    print("3. Post a tweet (when implemented)")
    print("4. View your recent tweets (when implemented)")
    print("5. Search tweets (when implemented)")
    
    # Test loading credentials
    print("\nTesting credential loading...")
    creds = load_x_credentials()
    
    if creds:
        print("\n✅ Credentials loaded successfully!")
        print("You can now use the X API functions in this script.")
        
        # Test connection
        print("\nTesting connection...")
        client = create_x_client()
        if client:
            try:
                me = client.get_me()
                if me.data:
                    print(f"✅ Successfully connected to X API as @{me.data.username}")
                else:
                    print("❌ Could not retrieve user information")
            except Exception as e:
                print(f"❌ Connection test failed: {e}")
        else:
            print("❌ Could not create X API client")
    else:
        print("\n❌ Could not load credentials. Please check your configuration.")