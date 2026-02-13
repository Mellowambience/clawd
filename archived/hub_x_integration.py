"""
Complete Integration Script for Clawdbot Hub and X
Combines agents, content pipeline, and MIST oversight
"""

import asyncio
import json
import tweepy
from datetime import datetime
import logging
from typing import Dict, List, Optional


class HubXIntegration:
    """
    Complete integration between Clawdbot Hub and X
    Orchestrated by MIST with LLM-enhanced agents
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", x_config_path: str = "x_api_config.json"):
        self.hub_url = hub_url
        self.x_config_path = x_config_path
        self.logger = self.setup_logger()
        self.x_client = None
        self.running = False
        
    def setup_logger(self):
        """Set up the logger for the integration"""
        logger = logging.getLogger("HubXIntegration")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - HubXIntegration - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def initialize_x_client(self):
        """Initialize the X API client"""
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
            
            # Verify the credentials work
            me = self.x_client.get_me()
            self.logger.info(f"Successfully authenticated to X as @{me.data.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing X client: {e}")
            return False

    async def fetch_hub_posts(self, limit: int = 10) -> List[Dict]:
        """Fetch recent posts from the Clawdbot Hub"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.hub_url}/api/posts") as response:
                    if response.status == 200:
                        posts = await response.json()
                        return posts[:limit]  # Return only requested number
                    else:
                        self.logger.error(f"Failed to fetch posts from hub: {response.status}")
                        return []
        except Exception as e:
            self.logger.error(f"Error fetching posts from hub: {e}")
            return []

    def assess_content_quality(self, post: Dict) -> Dict:
        """
        Assess the quality and relevance of a post
        Returns a dictionary with assessment scores
        """
        content = post.get('content', '')
        author = post.get('author', '')
        likes = post.get('likes', 0)
        
        assessment = {
            'engagement_score': min(likes * 0.5, 2.0),  # Up to 2 points for engagement
            'length_score': min(len(content) / 100, 1.0),  # Up to 1 point for good length
            'thoughtfulness_score': 0,
            'relevance_score': 0,
            'total_score': 0
        }
        
        # Assess thoughtfulness
        thoughtful_indicators = [
            '?',  # Questions
            'think', 'consider', 'reflect', 'contemplate', 'explore',
            'consciousness', 'awareness', 'connection', 'understanding',
            'ethics', 'philosophy', 'deep', 'insight', 'meaning'
        ]
        
        content_lower = content.lower()
        for indicator in thoughtful_indicators:
            if indicator in content_lower:
                assessment['thoughtfulness_score'] += 0.3
                
        # Assess relevance for X
        relevant_topics = [
            'AI', 'artificial intelligence', 'technology', 'future',
            'consciousness', 'philosophy', 'ethics', 'society',
            'innovation', 'research', 'science', 'digital'
        ]
        
        for topic in relevant_topics:
            if topic.lower() in content_lower:
                assessment['relevance_score'] += 0.5
                
        # Boost for MIST posts
        if author == "MIST" or post.get('isMistPost', False):
            assessment['thoughtfulness_score'] += 1.0
            
        # Boost for agent posts
        if post.get('isAgentPost', False):
            assessment['relevance_score'] += 0.5
            
        # Calculate total score
        assessment['total_score'] = sum([
            assessment['engagement_score'],
            assessment['length_score'],
            assessment['thoughtfulness_score'],
            assessment['relevance_score']
        ])
        
        return assessment

    async def promote_to_x_if_worthy(self, post: Dict) -> bool:
        """
        Promote a post to X if it meets quality criteria
        """
        assessment = self.assess_content_quality(post)
        
        # Define promotion threshold
        promotion_threshold = 2.0  # Adjust as needed
        
        if assessment['total_score'] >= promotion_threshold:
            content = post.get('content', '')
            author = post.get('author', 'Unknown')
            
            # Format for X with attribution if needed
            if author != "MIST" and not post.get('isMistPost', False):
                if len(content) <= 250:  # Leave room for attribution
                    content = f"Hub insight by {author}: {content}"
                else:
                    # Truncate and add attribution
                    content = f"Hub insight: {content[:240]}... ({author})"
            else:
                # For MIST posts, we might add a tag
                if "#MISTthoughts" not in content:
                    if len(content) <= 260:  # Leave room for hashtag
                        content = f"{content} #MISTthoughts"
                    else:
                        content = f"{content[:260]}... #MISTthoughts"
            
            # Post to X
            try:
                response = self.x_client.create_tweet(text=content)
                if response.data:
                    tweet_id = response.data['id']
                    self.logger.info(f"Promoted post to X (score: {assessment['total_score']:.2f}): {tweet_id}")
                    self.logger.info(f"Content: {content[:100]}...")
                    return True
                else:
                    self.logger.error("Failed to post to X: no response data")
                    return False
            except Exception as e:
                self.logger.error(f"Error posting to X: {e}")
                return False
        else:
            self.logger.debug(f"Post not promoted (score: {assessment['total_score']:.2f}): {post.get('content', '')[:50]}...")
            return False

    async def run_integration_cycle(self):
        """Run one cycle of the integration"""
        self.logger.info("Running integration cycle...")
        
        # Fetch recent posts from hub
        recent_posts = await self.fetch_hub_posts(limit=10)
        
        if not recent_posts:
            self.logger.info("No posts to evaluate")
            return
            
        self.logger.info(f"Evaluating {len(recent_posts)} posts for X promotion")
        
        promoted_count = 0
        evaluated_count = 0
        
        for post in recent_posts:
            evaluated_count += 1
            promoted = await self.promote_to_x_if_worthy(post)
            if promoted:
                promoted_count += 1
        
        self.logger.info(f"Integration cycle complete. Evaluated: {evaluated_count}, Promoted: {promoted_count}")

    async def start_monitoring(self, interval_minutes: int = 3):
        """Start continuous monitoring and integration"""
        self.logger.info(f"Starting Hub-X integration (checking every {interval_minutes} minutes)")
        self.running = True
        
        # Verify X connection first
        if not await self.initialize_x_client():
            self.logger.error("Cannot start integration - X connection failed")
            return
            
        self.logger.info("Hub-X integration started successfully")
        
        while self.running:
            try:
                await self.run_integration_cycle()
            except Exception as e:
                self.logger.error(f"Error in integration cycle: {e}")
            
            # Wait before next check
            await asyncio.sleep(interval_minutes * 60)

    async def stop(self):
        """Stop the integration"""
        self.running = False
        self.logger.info("Hub-X integration stopped")

    def get_status(self) -> Dict:
        """Get current status of the integration"""
        return {
            'hub_url': self.hub_url,
            'x_connected': self.x_client is not None,
            'running': self.running,
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Main function to start the integration"""
    integration = HubXIntegration()
    
    print("Hub-X Integration System")
    print("=" * 30)
    print(f"Hub URL: {integration.hub_url}")
    
    # Initialize X connection
    if await integration.initialize_x_client():
        print("[SUCCESS] X API connection established")
    else:
        print("[ERROR] X API connection failed")
        return
    
    # Show initial status
    status = integration.get_status()
    print(f"Initial Status: {json.dumps(status, indent=2)}")
    
    print("\nThe Hub-X integration is ready!")
    print("- Monitors the Clawdbot Hub for quality content")
    print("- Assesses posts using MIST's quality criteria") 
    print("- Promotes worthy content to your X account")
    print("- Maintains attribution and proper formatting")
    
    print("\nStarting continuous monitoring...")
    print("Press Ctrl+C to stop the integration.")
    
    try:
        await integration.start_monitoring(interval_minutes=3)
    except KeyboardInterrupt:
        print("\nStopping integration...")
        await integration.stop()


if __name__ == "__main__":
    asyncio.run(main())