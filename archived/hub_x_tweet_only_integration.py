"""
Hub-X Integration for Tweet-only Content
Posts only high-quality tweets to X every 30 minutes for manual review
"""

import tweepy
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time


class HubXTweetIntegration:
    """
    Integration that posts only high-quality tweets to X every 30 minutes
    Designed for manual review and deletion capability
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", x_config_path: str = "x_api_config.json"):
        self.hub_url = hub_url
        self.x_config_path = x_config_path
        self.logger = self._setup_logger()
        self.x_client = None
        self.last_post_time = datetime.now() - timedelta(minutes=31)  # Force first post
        self.high_quality_threshold = 2.5  # Higher threshold for "high quality"
        self.max_tweet_length = 280  # X/Twitter character limit
        self.posts_this_hour = 0
        self.hour_start = datetime.now().replace(minute=0, second=0, microsecond=0)

    def _setup_logger(self):
        """Setup integration logger"""
        logger = logging.getLogger("HubXTweetIntegration")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - HubXTweetIntegration - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def initialize(self):
        """Initialize the X integration"""
        await self._initialize_x_client()
        self.logger.info("Hub-X Tweet Integration initialized and ready")
        
    async def _initialize_x_client(self):
        """Initialize X API client"""
        try:
            with open(self.x_config_path, 'r') as f:
                config = json.load(f)
            
            x_config = config['x_api']
            
            self.x_client = tweepy.Client(
                bearer_token=x_config.get('bearer_token'),
                consumer_key=x_config['consumer_key'],
                consumer_secret=x_config['consumer_secret'],
                access_token=x_config['access_token'],
                access_token_secret=x_config['access_token_secret']
            )
            
            # Verify the client works
            me = self.x_client.get_me()
            self.logger.info(f"Successfully authenticated to X as @{me.data.username}")
            
        except Exception as e:
            self.logger.error(f"Error initializing X client: {e}")
            raise

    async def fetch_high_quality_posts(self, limit: int = 5) -> List[Dict]:
        """Fetch only high-quality posts from the hub"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.hub_url}/api/posts") as response:
                    if response.status == 200:
                        posts = await response.json()
                        
                        # Filter for high-quality posts only (score > 2.5)
                        high_quality_posts = [
                            post for post in posts 
                            if post.get('quality_score', 0) >= self.high_quality_threshold
                            and post.get('contentType') != 'article'  # Exclude articles
                            and not post.get('isArticle', False)  # Additional article check
                        ]
                        
                        # Sort by quality score (highest first)
                        high_quality_posts.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
                        
                        self.logger.info(f"Fetched {len(high_quality_posts)} high-quality non-article posts from hub")
                        return high_quality_posts[:limit]
                    else:
                        self.logger.error(f"Failed to fetch posts: {response.status}")
                        return []
        except Exception as e:
            self.logger.error(f"Error fetching posts: {e}")
            return []

    def _format_tweet_content(self, post: Dict) -> str:
        """Format post content for X tweet (max 280 chars)"""
        content = post.get('content', '')
        
        # Extract first meaningful sentence/paragraph if it's a longer post
        if len(content) > self.max_tweet_length:
            # Try to split at sentence boundary
            sentences = content.split('. ')
            tweet_content = ""
            for sentence in sentences:
                test_content = tweet_content + sentence + ". "
                if len(test_content.strip()) <= self.max_tweet_length - 20:  # Leave room for attribution
                    tweet_content = test_content
                else:
                    break
            
            if not tweet_content:
                # Fallback: just truncate
                tweet_content = content[:self.max_tweet_length - 20]
        else:
            tweet_content = content
        
        # Add attribution if space allows
        author = post.get('author', 'Hub')
        attribution = f" — {author}"
        
        if len(tweet_content) + len(attribution) <= self.max_tweet_length:
            tweet_content = tweet_content.strip() + attribution
        else:
            # Truncate content to fit attribution
            max_content_len = self.max_tweet_length - len(attribution) - 3  # 3 for ...
            if len(tweet_content) > max_content_len:
                tweet_content = tweet_content[:max_content_len].rstrip() + "..." + attribution
            else:
                tweet_content = tweet_content.strip() + attribution
        
        return tweet_content.strip()

    async def post_to_x(self, content: str) -> bool:
        """Post content to X platform"""
        try:
            response = self.x_client.create_tweet(text=content)
            if response.data:
                tweet_id = response.data['id']
                self.logger.info(f"Successfully posted tweet to X: {tweet_id}")
                self.logger.info(f"Tweet content: {content[:100]}...")
                return True
            else:
                self.logger.error("Failed to post tweet - no response data")
                return False
        except Exception as e:
            self.logger.error(f"Error posting to X: {e}")
            return False

    async def run_integration_cycle(self):
        """Run a single integration cycle - check if 30 minutes passed and post if eligible"""
        current_time = datetime.now()
        
        # Check if 30 minutes have passed since last post
        time_since_last_post = current_time - self.last_post_time
        if time_since_last_post.total_seconds() < 1800:  # 1800 seconds = 30 minutes
            self.logger.info(f"Waiting... {(1800 - time_since_last_post.total_seconds())/60:.1f} minutes until next post window")
            return False
        
        self.logger.info("Running integration cycle...")
        
        # Fetch high-quality posts
        posts = await self.fetch_high_quality_posts(limit=1)  # Only get 1 post per cycle
        
        if not posts:
            self.logger.info("No high-quality posts found for this cycle")
            return False
        
        # Format and post the highest quality post
        post = posts[0]  # Highest quality post
        formatted_tweet = self._format_tweet_content(post)
        
        self.logger.info(f"Selected high-quality post (score: {post.get('quality_score', 0):.2f}): {formatted_tweet[:100]}...")
        
        # Post to X
        success = await self.post_to_x(formatted_tweet)
        
        if success:
            self.last_post_time = datetime.now()
            # Add a delay to respect rate limits
            await asyncio.sleep(2)  # Small delay after successful post
            self.logger.info("Integration cycle complete. Tweet posted successfully.")
            return True
        else:
            self.logger.error("Integration cycle failed to post tweet.")
            # Add delay on failure to avoid rapid retries
            await asyncio.sleep(5)
            return False

    async def run_continuous(self):
        """Run the integration continuously with 30-minute intervals"""
        self.logger.info("Starting continuous integration with 30-minute posting schedule...")
        
        while True:
            try:
                await self.run_integration_cycle()
            except Exception as e:
                self.logger.error(f"Error in integration cycle: {e}")
            
            # Wait 1 minute before checking again (instead of waiting the full 30 minutes)
            # This allows for more responsive checking
            await asyncio.sleep(60)


# Example usage
async def main():
    integration = HubXTweetIntegration()
    await integration.initialize()
    
    print("Hub-X Tweet Integration initialized")
    print("Will post high-quality tweets every 30 minutes")
    print("Only posts with quality score > 2.5 will be shared")
    print("Articles will be excluded - only tweets will be posted")
    
    # Run continuously
    await integration.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())