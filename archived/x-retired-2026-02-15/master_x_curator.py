"""
Master X Platform Curator
Handles all curation responsibilities including optimized scheduling, 
monetization focus, and rate limit management
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
import pytz
from optimized_x_posting_schedule import OptimizedXScheduler
from implement_optimized_schedule import OptimizedHubXIntegration


class MasterXCurator:
    """
    Master curator that handles all X platform curation responsibilities
    including optimized scheduling, monetization focus, and rate limit management
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", x_config_path: str = "x_api_config.json"):
        self.hub_url = hub_url
        self.x_config_path = x_config_path
        self.logger = self._setup_logger()
        self.scheduler = OptimizedXScheduler(hub_url, x_config_path)
        self.integration = OptimizedHubXIntegration(hub_url, x_config_path)
        self.working_hours_active = True
        self.monetization_focus = True
        self.rate_limit_buffer = timedelta(minutes=5)  # Extra buffer beyond minimum

    def _setup_logger(self):
        """Setup curator logger"""
        logger = logging.getLogger("MasterXCurator")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - MasterXCurator - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def assess_platform_health(self) -> dict:
        """Assess the health and capacity of the X platform integration"""
        # Check rate limits
        now = datetime.now()
        time_since_last_post = now - self.scheduler.last_post_time
        rate_limit_ok = time_since_last_post >= (self.scheduler.min_post_interval - self.rate_limit_buffer)
        
        # Check optimal timing
        is_optimal, reason = self.scheduler.is_optimal_time()
        
        # Check content availability
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.hub_url}/api/posts") as response:
                    if response.status == 200:
                        posts = await response.json()
                        quality_posts = [p for p in posts if p.get('quality_score', 0) >= 2.7]
                        content_available = len(quality_posts) > 0
                    else:
                        content_available = False
        except:
            content_available = False
        
        return {
            'rate_limit_ok': rate_limit_ok,
            'is_optimal_time': is_optimal,
            'content_available': content_available,
            'should_post_now': rate_limit_ok and is_optimal and content_available,
            'next_optimal_time': self.scheduler.get_next_optimal_window(),
            'daily_progress': self.scheduler.get_daily_performance_report()
        }

    async def run_curatorial_decision_process(self):
        """Run the full curatorial decision process"""
        self.logger.info("Running curatorial decision process...")
        
        # Assess platform health
        health = await self.assess_platform_health()
        
        self.logger.info(f"Platform health: Rate OK={health['rate_limit_ok']}, "
                        f"Optimal={health['is_optimal_time']}, "
                        f"Content Available={health['content_available']}")
        
        if health['should_post_now']:
            self.logger.info("All conditions met, proceeding with post...")
            success = await self.integration.run_optimized_cycle()
            return success
        else:
            self.logger.info("Conditions not met for posting, will wait for next opportunity")
            
            # Log why we're not posting
            reasons = []
            if not health['rate_limit_ok']:
                reasons.append("rate limit not reached")
            if not health['is_optimal_time']:
                reasons.append(f"not optimal time ({self.scheduler.is_optimal_time()[1]})")
            if not health['content_available']:
                reasons.append("no quality content available")
            
            self.logger.info(f"Skipping post because: {', '.join(reasons)}")
            
            return False

    def get_working_hours_efficiency_report(self) -> dict:
        """Generate efficiency report for working hours optimization"""
        now = datetime.now(pytz.timezone('US/Eastern'))
        current_hour = now.hour
        current_weekday = now.weekday()
        
        # Determine current efficiency window
        if current_weekday >= 5:  # Weekend
            efficiency = "HIGH" if (self.scheduler.optimal_times['weekend_extended']['start'] <= 
                                  current_hour <= 
                                  self.scheduler.optimal_times['weekend_extended']['end']) else "LOW"
        else:  # Weekday
            efficiency = "LOW"  # Default to low
            for window_name, window in self.scheduler.optimal_times.items():
                if window_name != 'weekend_extended':  # Skip weekend window on weekdays
                    if window['start'] <= current_hour <= window['end']:
                        efficiency = "HIGH"
                        break
        
        return {
            'current_time': now.strftime('%H:%M %Z'),
            'current_day': now.strftime('%A'),
            'efficiency_level': efficiency,
            'next_high_efficiency_window': self.scheduler.get_next_optimal_window().strftime('%H:%M %Z on %A'),
            'daily_posts_completed': self.scheduler.posts_today,
            'daily_posts_remaining': max(0, self.scheduler.daily_limit - self.scheduler.posts_today),
            'monetization_focus': self.monetization_focus
        }

    async def run_curator_cycle(self):
        """Run a single curator cycle"""
        self.logger.info("Starting curator cycle...")
        
        # Run curatorial decision
        await self.run_curatorial_decision_process()
        
        # Generate efficiency report
        report = self.get_working_hours_efficiency_report()
        self.logger.info(f"Efficiency report: {report['efficiency_level']} efficiency, "
                        f"{report['daily_posts_remaining']} posts remaining today")
        
        return report

    async def start_curation_service(self):
        """Start the continuous curation service"""
        self.logger.info("🚀 Starting Master X Platform Curation Service")
        self.logger.info("=" * 60)
        self.logger.info("💼 CURATOR RESPONSIBILITIES:")
        self.logger.info("   • Optimized posting schedule for engagement")
        self.logger.info("   • Rate limit compliance and buffer management")
        self.logger.info("   • Monetization-focused content selection")
        self.logger.info("   • Working hours efficiency optimization")
        self.logger.info("   • Quality control and curation oversight")
        self.logger.info("=" * 60)
        
        # Initial efficiency report
        initial_report = self.get_working_hours_efficiency_report()
        self.logger.info(f"\n📊 INITIAL EFFICIENCY REPORT:")
        self.logger.info(f"   Current Time: {initial_report['current_time']}")
        self.logger.info(f"   Day: {initial_report['current_day']}")
        self.logger.info(f"   Efficiency: {initial_report['efficiency_level']}")
        self.logger.info(f"   Posts Remaining Today: {initial_report['daily_posts_remaining']}")
        self.logger.info(f"   Next High-Efficiency Window: {initial_report['next_high_efficiency_window']}")
        
        self.logger.info(f"\n🎯 MONETIZATION FOCUS: {initial_report['monetization_focus']}")
        self.logger.info("The curation service is now running and managing X platform optimization!")
        
        # Continuous operation
        while True:
            try:
                await self.run_curator_cycle()
            except Exception as e:
                self.logger.error(f"Error in curator cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
            
            # Wait 10 minutes between cycles (optimization balance)
            await asyncio.sleep(10 * 60)


# Example usage
async def main():
    curator = MasterXCurator()
    
    print("Master X Platform Curator")
    print("=" * 40)
    print("Handles optimized scheduling, monetization focus, and rate limit management")
    
    # Show initial report
    report = curator.get_working_hours_efficiency_report()
    print(f"\nCurrent Status:")
    print(f"  Time: {report['current_time']}")
    print(f"  Efficiency: {report['efficiency_level']}")
    print(f"  Posts Remaining: {report['daily_posts_remaining']}")
    
    # Start the curator service
    await curator.start_curation_service()


if __name__ == "__main__":
    asyncio.run(main())