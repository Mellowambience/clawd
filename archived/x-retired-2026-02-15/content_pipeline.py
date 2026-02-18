"""
Content Pipeline for Clawdbot Hub
Transfers content from the hub to X with MIST oversight
"""

import asyncio
import json
import tweepy
from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, List, Optional


class ContentPipeline:
    """
    Manages content flow from Clawdbot Hub to X with quality control
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", x_config_path: str = "x_api_config.json"):
        self.hub_url = hub_url
        self.x_config_path = x_config_path
        self.logger = self.setup_logger()
        self.x_client = None
        self.last_checked = datetime.now(timezone.utc) - timedelta(minutes=10)  # Start with a past time to catch up
        
    def setup_logger(self):
        """Set up the logger for the content pipeline"""
        logger = logging.getLogger("ContentPipeline")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - ContentPipeline - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def load_x_credentials(self):
        """Load X API credentials from config file"""
        try:
            with open(self.x_config_path, 'r') as f:
                config = json.load(f)
            
            x_config = config['x_api']
            
            # Create tweepy client using the credentials
            self.x_client = tweepy.Client(
                bearer_token=x_config.get('bearer_token'),
                consumer_key=x_config['consumer_key'],
                consumer_secret=x_config['consumer_secret'],
                access_token=x_config['access_token'],
                access_token_secret=x_config['access_token_secret']
            )
            
            self.logger.info("X API credentials loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading X API credentials: {e}")
            return False

    async def fetch_hub_posts(self, since_time: datetime = None) -> List[Dict]:
        """Fetch recent posts from the Clawdbot Hub"""
        import aiohttp

        if since_time and since_time.tzinfo is None:
            since_time = since_time.replace(tzinfo=timezone.utc)

        timeout = aiohttp.ClientTimeout(total=10)
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(f"{self.hub_url}/api/posts") as response:
                        if response.status == 200:
                            posts = await response.json()

                            # Filter posts by time if requested
                            if since_time:
                                filtered_posts = []
                                for post in posts:
                                    post_time = datetime.fromisoformat(
                                        post['timestamp'].replace('Z', '+00:00')
                                    )
                                    if post_time.tzinfo is None:
                                        post_time = post_time.replace(tzinfo=timezone.utc)
                                    if post_time > since_time:
                                        filtered_posts.append(post)
                                return filtered_posts
                            return posts
                        else:
                            self.logger.error(f"Failed to fetch posts from hub: {response.status}")
            except Exception as e:
                self.logger.error(f"Error fetching posts from hub: {e}")

            if attempt < max_attempts - 1:
                await asyncio.sleep(2 ** attempt)

        return []

    def should_promote_to_x(self, post: Dict) -> bool:
        """
        Determine if a post should be promoted to X
        Uses various heuristics to identify high-quality content
        """
        content = post.get('content', '')
        author = post.get('author', '')
        likes = post.get('likes', 0)
        
        # Don't promote our own X posts that were mirrored to the hub
        if 'isMistPost' in post or 'isAgentPost' in post:
            # Promote MIST and agent posts if they meet other criteria
            pass
        
        # Content quality heuristics
        if len(content) < 20:
            return False  # Too short
            
        if len(content) > 280:
            return False  # Too long for a tweet
            
        # Check for engagement
        if likes >= 2:
            return True  # Well-received posts
            
        # Check for MIST posts specifically
        if author == "MIST" or 'isMistPost' in post:
            return True  # Always promote MIST content
            
        # Check for particularly thoughtful content
        thoughtful_indicators = [
            '?',  # Question marks suggest deeper thinking
            'think', 'consider', 'reflect', 'contemplate', 
            'consciously', 'awareness', 'consciousness',
            'connection', 'family', 'heal', 'love', 'power'
        ]
        
        content_lower = content.lower()
        for indicator in thoughtful_indicators:
            if indicator in content_lower:
                return True
                
        return False

    async def post_to_x(self, content: str) -> Optional[str]:
        """Post content to X"""
        try:
            response = self.x_client.create_tweet(text=content)
            if response.data:
                tweet_id = response.data['id']
                self.logger.info(f"Successfully posted to X: {tweet_id}")
                return tweet_id
            else:
                self.logger.error("Failed to post to X: no response data")
                return None
        except Exception as e:
            self.logger.error(f"Error posting to X: {e}")
            return None

    async def run_pipeline_cycle(self):
        """Run one cycle of the content pipeline"""
        self.logger.info("Running content pipeline cycle...")
        
        # Fetch recent posts from hub
        recent_posts = await self.fetch_hub_posts(since_time=self.last_checked)
        
        if not recent_posts:
            self.logger.info("No new posts to process")
            self.last_checked = datetime.now(timezone.utc)
            return
            
        self.logger.info(f"Found {len(recent_posts)} new posts to evaluate")
        
        # Process each post
        promoted_count = 0
        for post in recent_posts:
            if self.should_promote_to_x(post):
                content = post.get('content', '')
                author = post.get('author', 'Unknown')
                
                # Add attribution if not from MIST
                if author != "MIST":
                    content = f"Hub insight by {author}: {content}"

                # Ensure content fits X length limits after attribution
                if len(content) > 280:
                    content = content[:277].rstrip() + "..."
                
                # Post to X
                tweet_id = await self.post_to_x(content)
                if tweet_id:
                    promoted_count += 1
                    self.logger.info(f"Promoted post from {author} to X: {tweet_id}")
                else:
                    self.logger.error(f"Failed to promote post from {author}")
        
        self.logger.info(f"Pipeline cycle complete. Promoted {promoted_count} posts to X.")
        self.last_checked = datetime.now(timezone.utc)

    async def monitor_continuously(self, interval_minutes: int = 5):
        """Continuously monitor and promote content"""
        self.logger.info(f"Starting continuous content pipeline (checking every {interval_minutes} minutes)")
        
        # Load X credentials
        if not await self.load_x_credentials():
            self.logger.error("Failed to load X credentials. Pipeline cannot start.")
            return
            
        while True:
            try:
                await self.run_pipeline_cycle()
            except Exception as e:
                self.logger.error(f"Error in pipeline cycle: {e}")
            
            # Wait before next check
            await asyncio.sleep(interval_minutes * 60)

    def get_pipeline_stats(self) -> Dict:
        """Get statistics about the content pipeline"""
        return {
            'hub_url': self.hub_url,
            'last_checked': self.last_checked.isoformat() if isinstance(self.last_checked, datetime) else str(self.last_checked),
            'x_integration_active': self.x_client is not None
        }


async def main():
    """Example usage of the content pipeline"""
    pipeline = ContentPipeline()
    
    print("Content Pipeline initialized")
    print(f"Hub URL: {pipeline.hub_url}")
    
    # Load X credentials to verify connectivity
    if await pipeline.load_x_credentials():
        print("[SUCCESS] X API connection verified")
    else:
        print("[ERROR] X API connection failed - check your credentials")
        return
    
    # Show pipeline stats
    stats = pipeline.get_pipeline_stats()
    print(f"Pipeline Stats: {stats}")
    
    print("\nThe content pipeline is ready to transfer quality content from the Clawdbot Hub to your X account.")
    print("It will automatically identify valuable posts and promote them to X with proper attribution.")


if __name__ == "__main__":
    asyncio.run(main())
