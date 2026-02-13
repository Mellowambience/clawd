"""
Implement Optimized X Platform Schedule
Integrates optimized posting schedule with the existing Hub-X integration
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
import pytz
from optimized_x_posting_schedule import OptimizedXScheduler


class OptimizedHubXIntegration:
    """
    Hub-X integration with optimized scheduling for monetization-focused posting
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", x_config_path: str = "x_api_config.json"):
        self.hub_url = hub_url
        self.x_config_path = x_config_path
        self.logger = self._setup_logger()
        self.scheduler = OptimizedXScheduler(hub_url, x_config_path)
        self.high_quality_threshold = 2.7  # Increased threshold for monetization focus
        self.max_tweet_length = 280
        self.posts_this_hour = 0
        self.hour_start = datetime.now().replace(minute=0, second=0, microsecond=0)

    def _setup_logger(self):
        """Setup integration logger"""
        logger = logging.getLogger("OptimizedHubXIntegration")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - OptimizedHubXIntegration - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def fetch_monetizable_content(self, limit: int = 5) -> list:
        """Fetch content that's likely to drive monetization"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.hub_url}/api/posts") as response:
                    if response.status == 200:
                        posts = await response.json()
                        
                        # Filter for monetization-appropriate content
                        monetizable_posts = []
                        for post in posts:
                            # Higher quality threshold for monetization
                            if (post.get('quality_score', 0) >= self.high_quality_threshold and
                                post.get('contentType') != 'article' and
                                not post.get('isArticle', False)):
                                
                                # Check for engagement indicators
                                engagement_score = self._calculate_engagement_potential(post)
                                if engagement_score >= 0.6:  # High engagement potential
                                    post['engagement_potential'] = engagement_score
                                    monetizable_posts.append(post)
                        
                        # Sort by engagement potential and quality score
                        monetizable_posts.sort(
                            key=lambda x: (x.get('engagement_potential', 0), x.get('quality_score', 0)), 
                            reverse=True
                        )
                        
                        self.logger.info(f"Fetched {len(monetizable_posts)} monetization-appropriate posts from hub")
                        return monetizable_posts[:limit]
                    else:
                        self.logger.error(f"Failed to fetch posts: {response.status}")
                        return []
        except Exception as e:
            self.logger.error(f"Error fetching monetizable posts: {e}")
            return []

    def _calculate_engagement_potential(self, post: dict) -> float:
        """Calculate engagement potential for monetization"""
        content = post.get('content', '').lower()
        
        # Engagement indicators
        engagement_indicators = [
            ('question', content.count('?') * 0.2),
            ('call_to_action', 0.15 if any(word in content for word in ['learn', 'read', 'discover', 'explore', 'try', 'follow']) else 0),
            ('controversial_or_debatable', 0.2 if any(word in content for word in ['should', 'could', 'maybe', 'perhaps', 'argue', 'debate']) else 0),
            ('value_proposition', 0.2 if any(word in content for word in ['tip', 'insight', 'guide', 'advice', 'strategy', 'secret', 'hack']) else 0),
            ('curiosity_gap', 0.15 if any(word in content for word in ['why', 'how', 'what', 'surprising', 'unexpected', 'shocking']) else 0),
            ('length_factor', min(len(content) / 500, 0.1))  # Longer content tends to engage more
        ]
        
        total_score = sum(score for _, score in engagement_indicators)
        return min(total_score, 1.0)

    def _format_monetizable_tweet(self, post: dict) -> str:
        """Format post content for monetization-focused X post"""
        content = post.get('content', '')
        
        # Extract key points for engagement
        if len(content) > self.max_tweet_length:
            # Try to extract the most engaging part
            sentences = content.split('. ')
            tweet_content = ""
            for sentence in sentences:
                test_content = tweet_content + sentence + ". "
                if len(test_content.strip()) <= self.max_tweet_length - 30:  # Leave room for engagement elements
                    tweet_content = test_content
                else:
                    break
            
            if not tweet_content:
                tweet_content = content[:self.max_tweet_length - 50]
        else:
            tweet_content = content
        
        # Add engagement hooks for monetization
        engagement_hooks = [
            "\n\nWhat do you think?",
            "\n\nWould you agree?",
            "\n\nInteresting perspective?",
            "\n\nFood for thought...",
            "\n\nShare your view!"
        ]
        
        import random
        hook = random.choice(engagement_hooks)
        
        # Add author attribution and engagement hook
        author = post.get('author', 'Hub')
        final_content = tweet_content.strip()
        
        if len(final_content) + len(f" — {author}{hook}") <= self.max_tweet_length:
            final_content = final_content + f" — {author}{hook}"
        else:
            # Truncate to fit everything
            max_content_len = self.max_tweet_length - len(f" — {author}{hook}") - 3
            if len(final_content) > max_content_len:
                final_content = final_content[:max_content_len].rstrip() + "..." + f" — {author}{hook}"
            else:
                final_content = final_content.strip() + f" — {author}{hook}"
        
        return final_content.strip()

    async def run_optimized_cycle(self):
        """Run an optimized posting cycle"""
        self.logger.info("Running optimized posting cycle...")
        
        # Check if we should post now
        should_post = await self.scheduler.should_post_now()
        if not should_post:
            self.logger.info("Not optimal time to post, skipping cycle")
            return False
        
        # Fetch monetization-appropriate content
        posts = await self.fetch_monetizable_content(limit=1)
        if not posts:
            self.logger.info("No monetization-appropriate content found")
            return False
        
        post = posts[0]  # Get highest potential post
        formatted_tweet = self._format_monetizable_tweet(post)
        
        self.logger.info(f"Selected monetization-focused post (score: {post.get('quality_score', 0):.2f}, engagement: {post.get('engagement_potential', 0):.2f}): {formatted_tweet[:80]}...")
        
        # Post to X (would implement actual posting here)
        # For now, we'll just log that we would post
        self.logger.info(f"WOULD POST to X: {formatted_tweet[:100]}...")
        
        # Update counters
        self.scheduler.increment_post_counter()
        
        # Update last post time
        from optimized_x_posting_schedule import datetime
        self.scheduler.last_post_time = datetime.now()
        
        self.logger.info("Optimized cycle completed successfully")
        return True

    async def run_continuous_optimization(self):
        """Run the optimized integration continuously"""
        self.logger.info("Starting optimized X posting with monetization focus...")
        self.logger.info("Schedule: Posting during optimal engagement windows")
        self.logger.info("Threshold: High-quality content only (score > 2.7)")
        self.logger.info("Focus: Monetization-appropriate content with engagement hooks")
        
        while True:
            try:
                await self.run_optimized_cycle()
            except Exception as e:
                self.logger.error(f"Error in optimized cycle: {e}")
            
            # Wait 15 minutes between checks to reduce API calls
            await asyncio.sleep(15 * 60)


# Example usage
async def main():
    integration = OptimizedHubXIntegration()
    
    print("Optimized X Platform Integration for Monetization")
    print("=" * 60)
    
    # Show current schedule status
    is_optimal, reason = integration.scheduler.is_optimal_time()
    print(f"Current time optimal: {is_optimal} ({reason})")
    
    # Show daily plan
    report = integration.scheduler.get_daily_performance_report()
    print(f"\nDaily Plan: {report['posts_scheduled']} max posts")
    print(f"Completed: {report['posts_completed']}")
    print(f"Remaining: {report['remaining_posts']}")
    
    print("\nOptimal Windows:")
    for window in report['optimal_windows_available']:
        print(f"  • {window}")
    
    # Start continuous operation
    await integration.run_continuous_optimization()


if __name__ == "__main__":
    asyncio.run(main())