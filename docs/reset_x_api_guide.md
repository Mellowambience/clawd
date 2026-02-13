# X API Reset Guide

## Issue Identified
Your current X API credentials are mismatched, causing authentication failures. The access tokens do not correspond to the consumer credentials in your configuration.

## Recommended Solution: Create New App

### Step 1: Create a New X Developer App
1. Go to https://developer.twitter.com/
2. Sign in to your account
3. Click on "Create Project" or "Create App"
4. Fill in the project details:
   - Project name: Choose something descriptive
   - Project use case: Select appropriately
   - Tell them about your project: Provide honest details
5. Wait for approval if required

### Step 2: Generate Fresh Credentials
1. Once approved, navigate to your app's dashboard
2. Go to the "Keys and tokens" section
3. Under "API Key and Secret", copy both values:
   - API Key (this is your consumer_key)
   - API Secret (this is your consumer_secret)
4. Under "Access Token and Secret", click "Generate":
   - Access Token (this is your access_token)
   - Access Token Secret (this is your access_token_secret)
5. Also generate a Bearer Token under the "Authentication Tokens" section

### Step 3: Update Configuration
Replace the content of `C:\Users\nator\clawd\x_api_config.json` with:

```json
{
  "x_api": {
    "consumer_key": "YOUR_NEW_API_KEY",
    "consumer_secret": "YOUR_NEW_API_SECRET",
    "access_token": "YOUR_NEW_ACCESS_TOKEN",
    "access_token_secret": "YOUR_NEW_ACCESS_TOKEN_SECRET",
    "bearer_token": "YOUR_NEW_BEARER_TOKEN"
  }
}
```

### Step 4: Verify Setup
Run the following command to test:
```bash
python -c "
import tweepy
import json
from pathlib import Path

config_file = Path('C:/Users/nator/clawd/x_api_config.json')
with open(config_file, 'r') as f:
    config = json.load(f)

x_config = config['x_api']
client = tweepy.Client(
    bearer_token=x_config['bearer_token'],
    consumer_key=x_config['consumer_key'],
    consumer_secret=x_config['consumer_secret'],
    access_token=x_config['access_token'],
    access_token_secret=x_config['access_token_secret']
)

me = client.get_me()
print(f'Successfully authenticated as @{me.data.username}')
"
```

## Alternative: Use Application-Only Authentication
If you only need to read public data, you can use Bearer Token authentication alone:

```python
import tweepy

client = tweepy.Client(bearer_token='YOUR_BEARER_TOKEN')

# Example: Search for recent tweets
tweets = client.search_recent_tweets(query='python', max_results=10)
for tweet in tweets.data:
    print(tweet.text)
```

## Troubleshooting Tips
- Ensure all credentials come from the same X Developer App
- Check for extra spaces or special characters when copying credentials
- Verify your X Developer App has the correct permissions enabled
- Make sure your X account meets the requirements for API access

Once you've created a new properly-configured app, all the tools and scripts we've created will work seamlessly.