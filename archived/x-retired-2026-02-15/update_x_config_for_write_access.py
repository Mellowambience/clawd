"""
Update X API configuration for write access
Instructions for setting up complete X API access with proper permissions
"""

import json
import tweepy


def check_and_verify_full_access():
    """
    Verify that all X API credentials are properly configured for write access
    """
    try:
        # Load the current config
        with open('x_api_config.json', 'r') as f:
            config = json.load(f)
        
        print("Current X API Configuration:")
        print(json.dumps(config, indent=2))
        
        x_config = config['x_api']
        
        # Create a client with all credentials
        client = tweepy.Client(
            bearer_token=x_config.get('bearer_token'),
            consumer_key=x_config['consumer_key'],
            consumer_secret=x_config['consumer_secret'],
            access_token=x_config['access_token'],
            access_token_secret=x_config['access_token_secret']
        )
        
        print("\nVerifying X API access levels...")
        
        # Test basic authentication
        try:
            me = client.get_me()
            print(f"[OK] Authenticated as: @{me.data.username}")
            print(f"  User ID: {me.data.id}")
            print(f"  Account name: {me.data.name}")
        except Exception as e:
            print(f"[ERROR] Authentication failed: {e}")
            return False
        
        # Test read capabilities
        try:
            tweets = client.get_users_tweets(id=me.data.id, max_results=1)
            print("[OK] Read access confirmed")
        except Exception as e:
            print(f"[ERROR] Read access failed: {e}")
            return False
        
        # Test write capabilities (the crucial part)
        try:
            # Attempt to create a test tweet
            test_tweet = client.create_tweet(
                text="Testing write permissions for Clawdbot Hub integration"
            )
            print(f"[OK] Write access confirmed - Test tweet ID: {test_tweet.data['id']}")
            
            # Clean up the test tweet immediately
            delete_result = client.delete_tweet(test_tweet.data['id'])
            print("[OK] Test tweet cleaned up successfully")
            
        except tweepy.Forbidden as e:
            print(f"[ERROR] Write access denied: {e}")
            print("\nINSTRUCTIONS TO FIX:")
            print("1. Go to https://developer.twitter.com/en/portal/projects/")
            print("2. Select your project and app")
            print("3. Click on 'App settings'")
            print("4. Under 'User authentication settings', ensure:")
            print("   - Type of App: Choose 'Native App', 'Web App', or 'Public App'") 
            print("   - App permissions: Select 'Read and Write' (NOT just 'Read')")
            print("   - OAuth 2.0 Authorization Method: Select 'PKCE with Proof Key for Code Exchange'")
            print("5. Save the settings")
            print("6. If prompted, regenerate your access tokens with the new permissions")
            print("7. Update x_api_config.json if new tokens are generated")
            return False
        except Exception as e:
            print(f"[ERROR] Write access test failed with error: {e}")
            return False
        
        print("\n[SUCCESS] All X API permissions are properly configured!")
        print("The Clawdbot Hub integration can now post to X automatically.")
        return True
        
    except FileNotFoundError:
        print("x_api_config.json file not found!")
        return False
    except json.JSONDecodeError:
        print("Invalid JSON in x_api_config.json")
        return False
    except Exception as e:
        print(f"Error checking X API access: {e}")
        return False


def generate_oauth_setup_guide():
    """
    Generate a complete guide for setting up X API with proper permissions
    """
    guide = """
X API Setup Guide for Clawdbot Hub Integration
=============================================

To enable the Clawdbot Hub to automatically post quality content to X:

1. LOG INTO X DEVELOPER PORTAL
   - Go to: https://developer.twitter.com/en/portal/dashboard
   - Sign in with your X account

2. LOCATE YOUR APP
   - From the dashboard, select your project
   - Select your app from the project view

3. UPDATE APP PERMISSIONS
   - Click on "App settings"
   - Find "User authentication settings" section
   - Click "Edit" next to permissions
   - SELECT "READ AND WRITE" (very important!)
   - Save the changes

4. REGENERATE ACCESS TOKENS (if required)
   - After changing permissions, you may need to regenerate:
   - Access Token and Secret
   - These will appear in the "Keys and tokens" section
   - Update x_api_config.json with new values if they change

5. TEST THE INTEGRATION
   - Run: python verify_x_permissions.py
   - Should show success for both read and write operations

6. LAUNCH THE INTEGRATION
   - Run: python hub_x_integration.py
   - The system will begin monitoring the hub and posting quality content to X

IMPORTANT: The app must have "Read and Write" permissions for the content pipeline to function.
"""
    
    print(guide)
    with open("x_api_setup_guide.txt", "w") as f:
        f.write(guide)
    print("Setup guide saved to x_api_setup_guide.txt")


if __name__ == "__main__":
    print("Checking X API configuration for write access...\n")
    
    success = check_and_verify_full_access()
    
    if not success:
        print("\n" + "="*60)
        print("GENERATING SETUP GUIDE...")
        print("="*60)
        generate_oauth_setup_guide()
    else:
        print("\nYour X API is fully configured for the Clawdbot Hub integration!")