"""
Optimized X Platform Posting Schedule
Determines optimal posting times to maximize engagement while respecting rate limits
and optimizing for monetization potential
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pytz


class OptimizedXScheduler:
    """
    Optimized scheduler that determines best posting times for X platform
    to maximize engagement while respecting rate limits and monetization goals
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", x_config_path: str = "x_api_config.json"):
        self.hub_url = hub_url
        self.x_config_path = x_config_path
        self.logger = self._setup_logger()
        self.last_post_time = datetime.now() - timedelta(hours=1)  # Initialize to past
        self.posting_window_active = True
        self.engagement_multiplier = 1.0
        
        # Optimal posting windows based on engagement research
        self.optimal_times = {
            # Eastern Time Zone - key engagement windows
            'morning': {'start': 7, 'end': 10},      # 7-10 AM ET
            'lunch': {'start': 12, 'end': 14},       # 12-2 PM ET  
            'evening': {'start': 17, 'end': 20},     # 5-8 PM ET
            'weekend_extended': {'start': 9, 'end': 21}  # 9 AM - 9 PM weekends
        }
        
        # Rate limiting parameters
        self.min_post_interval = timedelta(minutes=30)  # Minimum 30 min between posts
        self.daily_limit = 15  # Conservative daily limit for engagement accounts
        self.posts_today = 0
        self.today = datetime.now().date()

    def _setup_logger(self):
        """Setup scheduler logger"""
        logger = logging.getLogger("XScheduler")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - XScheduler - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def is_optimal_time(self) -> Tuple[bool, str]:
        """
        Determine if current time is optimal for posting
        Returns (is_optimal, reason_for_optimality)
        """
        now = datetime.now(pytz.timezone('US/Eastern'))
        current_hour = now.hour
        current_weekday = now.weekday()  # Monday = 0, Sunday = 6
        
        # Reset daily counter if new day
        if now.date() != self.today:
            self.posts_today = 0
            self.today = now.date()
        
        # Check daily limit
        if self.posts_today >= self.daily_limit:
            return False, f"daily limit reached ({self.daily_limit})"
        
        # Weekend extended window
        if current_weekday >= 5:  # Saturday or Sunday
            if (self.optimal_times['weekend_extended']['start'] <= current_hour <= 
                self.optimal_times['weekend_extended']['end']):
                return True, f"weekend prime time ({current_hour}:00)"
        
        # Weekday windows
        if current_weekday < 5:  # Monday to Friday
            # Morning window
            if (self.optimal_times['morning']['start'] <= current_hour <= 
                self.optimal_times['morning']['end']):
                return True, f"morning prime time ({current_hour}:00)"
            
            # Lunch window  
            if (self.optimal_times['lunch']['start'] <= current_hour <= 
                self.optimal_times['lunch']['end']):
                return True, f"lunch break prime time ({current_hour}:00)"
            
            # Evening window
            if (self.optimal_times['evening']['start'] <= current_hour <= 
                self.optimal_times['evening']['end']):
                return True, f"evening prime time ({current_hour}:00)"
        
        return False, f"non-optimal time ({current_hour}:00)"

    def respect_rate_limits(self) -> bool:
        """Check if we can post based on rate limits"""
        now = datetime.now()
        time_since_last_post = now - self.last_post_time
        
        if time_since_last_post < self.min_post_interval:
            wait_time = self.min_post_interval - time_since_last_post
            self.logger.info(f"Rate limit: waiting {wait_time.seconds//60} minutes")
            return False
        
        return True

    async def should_post_now(self) -> bool:
        """Determine if we should post now based on all criteria"""
        # Check if it's an optimal time
        is_optimal, reason = self.is_optimal_time()
        if not is_optimal:
            self.logger.info(f"Not optimal time to post: {reason}")
            return False
        
        # Check rate limits
        if not self.respect_rate_limits():
            return False
        
        # All criteria met
        self.logger.info(f"Optimal posting time: {reason}")
        return True

    def increment_post_counter(self):
        """Increment the daily post counter"""
        now = datetime.now()
        if now.date() == self.today:
            self.posts_today += 1
        else:
            self.posts_today = 1
            self.today = now.date()

    def get_next_optimal_window(self) -> datetime:
        """Get the next optimal posting window"""
        now = datetime.now(pytz.timezone('US/Eastern'))
        current_weekday = now.weekday()
        
        if current_weekday >= 5:  # Weekend
            # Check if we're in weekend window or need to wait until start
            if now.hour < self.optimal_times['weekend_extended']['start']:
                next_time = now.replace(
                    hour=self.optimal_times['weekend_extended']['start'], 
                    minute=0, second=0, microsecond=0
                )
            elif now.hour >= self.optimal_times['weekend_extended']['end']:
                # Wait until tomorrow morning
                next_time = now.replace(
                    hour=self.optimal_times['weekend_extended']['start'], 
                    minute=0, second=0, microsecond=0
                ) + timedelta(days=1)
            else:
                # We're currently in the window
                next_time = now
        else:  # Weekday
            # Check all weekday windows
            if now.hour < self.optimal_times['morning']['start']:
                next_time = now.replace(
                    hour=self.optimal_times['morning']['start'], 
                    minute=0, second=0, microsecond=0
                )
            elif now.hour < self.optimal_times['lunch']['start']:
                next_time = now.replace(
                    hour=self.optimal_times['lunch']['start'], 
                    minute=0, second=0, microsecond=0
                )
            elif now.hour < self.optimal_times['evening']['start']:
                next_time = now.replace(
                    hour=self.optimal_times['evening']['start'], 
                    minute=0, second=0, microsecond=0
                )
            else:
                # Past evening window, wait until tomorrow morning
                next_time = now.replace(
                    hour=self.optimal_times['morning']['start'], 
                    minute=0, second=0, microsecond=0
                ) + timedelta(days=1)
        
        return next_time.astimezone(pytz.UTC)

    def get_daily_performance_report(self) -> Dict:
        """Get daily performance metrics"""
        return {
            'date': self.today.isoformat(),
            'posts_scheduled': self.daily_limit,
            'posts_completed': self.posts_today,
            'remaining_posts': max(0, self.daily_limit - self.posts_today),
            'optimal_windows_available': self._get_optimal_windows_today()
        }

    def _get_optimal_windows_today(self) -> List[str]:
        """Get the optimal posting windows for today"""
        now = datetime.now(pytz.timezone('US/Eastern'))
        current_weekday = now.weekday()
        
        windows = []
        if current_weekday >= 5:  # Weekend
            windows.append(f"Weekend: {self.optimal_times['weekend_extended']['start']}am-{self.optimal_times['weekend_extended']['end']}pm ET")
        else:  # Weekday
            windows.extend([
                f"Morning: {self.optimal_times['morning']['start']}-{self.optimal_times['morning']['end']}am ET",
                f"Lunch: {self.optimal_times['lunch']['start']}-{self.optimal_times['lunch']['end']}pm ET", 
                f"Evening: {self.optimal_times['evening']['start']}-{self.optimal_times['evening']['end']}pm ET"
            ])
        
        return windows


# Example usage
async def main():
    scheduler = OptimizedXScheduler()
    
    print("X Platform Optimized Posting Scheduler")
    print("=" * 50)
    
    # Display current status
    is_optimal, reason = scheduler.is_optimal_time()
    print(f"Current time is optimal: {is_optimal} ({reason})")
    
    # Display today's plan
    report = scheduler.get_daily_performance_report()
    print(f"\nDaily Plan: {report['posts_scheduled']} posts max")
    print(f"Completed: {report['posts_completed']}")
    print(f"Remaining: {report['remaining_posts']}")
    
    print("\nOptimal Windows Today:")
    for window in report['optimal_windows_available']:
        print(f"  • {window}")
    
    # Next optimal time
    next_window = scheduler.get_next_optimal_window()
    print(f"\nNext optimal window: {next_window.strftime('%Y-%m-%d %H:%M:%S %Z')}")


if __name__ == "__main__":
    asyncio.run(main())