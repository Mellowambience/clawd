"""
X Platform Research Agent
Monitors X platform for research insights and relays findings to Clawdbot Hub
"""

import tweepy
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re


class XResearchAgent:
    """
    Agent that researches X platform to gather insights and relay them to Clawdbot Hub
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", x_config_path: str = "x_api_config.json"):
        self.hub_url = hub_url
        self.x_config_path = x_config_path
        self.logger = self._setup_logger()
        self.x_client = None
        self.research_keywords = [
            'AI', 'artificial intelligence', 'consciousness', 'ethics', 'technology',
            'philosophy', 'future', 'innovation', 'research', 'science', 'digital',
            'awareness', 'mind', 'cognition', 'neural', 'learning', 'automation',
            'transparency', 'bias', 'fairness', 'responsibility', 'governance'
        ]
        self.last_research_time = datetime.now() - timedelta(minutes=10)
        
    def _setup_logger(self):
        """Setup agent logger"""
        logger = logging.getLogger("XResearchAgent")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - XResearchAgent - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def initialize(self):
        """Initialize the X research agent"""
        await self._initialize_x_client()
        self.logger.info("X Research Agent initialized and ready for platform research")
        
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

    async def search_x_platform(self, query: str = None, max_results: int = 20) -> List[Dict]:
        """Search X platform for relevant research content"""
        if not query:
            # Use research keywords
            query = " OR ".join(self.research_keywords[:5])  # Use first 5 keywords
        
        query += " -is:retweet lang:en"  # Exclude retweets, English only
        
        try:
            tweets = self.x_client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations']
            )
            
            if tweets.data:
                tweet_list = []
                for tweet in tweets.data:
                    tweet_data = {
                        'id': tweet.id,
                        'text': tweet.text,
                        'author_id': tweet.author_id,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                        'hashtag_symbols': self._extract_hashtags(tweet.text)
                    }
                    tweet_list.append(tweet_data)
                
                self.logger.info(f"Found {len(tweet_list)} relevant tweets for research")
                return tweet_list
            else:
                self.logger.info("No tweets found for research query")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching X platform: {e}")
            return []

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from tweet text"""
        return re.findall(r'#\w+', text)

    async def analyze_research_findings(self, tweets: List[Dict]) -> Dict[str, Any]:
        """Analyze research findings from X platform"""
        if not tweets:
            return {}
        
        # Analyze engagement metrics
        total_engagement = 0
        high_engagement_tweets = []
        
        for tweet in tweets:
            metrics = tweet.get('metrics', {})
            engagement = (
                metrics.get('like_count', 0) + 
                metrics.get('retweet_count', 0) + 
                metrics.get('reply_count', 0) + 
                metrics.get('quote_count', 0)
            )
            
            if engagement > 10:  # High engagement threshold
                high_engagement_tweets.append(tweet)
            
            total_engagement += engagement
        
        # Extract key themes/topics
        themes = {}
        for tweet in tweets:
            text = tweet['text'].lower()
            for keyword in self.research_keywords:
                if keyword.lower() in text:
                    themes[keyword] = themes.get(keyword, 0) + 1
        
        analysis = {
            'total_tweets': len(tweets),
            'total_engagement': total_engagement,
            'high_engagement_tweets': len(high_engagement_tweets),
            'key_themes': themes,
            'top_tweets': sorted(tweets, key=lambda x: x.get('metrics', {}).get('like_count', 0), reverse=True)[:5],
            'research_summary': self._generate_research_summary(themes, len(tweets))
        }
        
        return analysis

    def _generate_research_summary(self, themes: Dict[str, int], total_tweets: int) -> str:
        """Generate a summary of research findings"""
        if not themes:
            return "No significant themes identified in recent X platform research."
        
        top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:3]
        theme_str = ", ".join([f"{theme}({count})" for theme, count in top_themes])
        
        return f"X platform research identified key themes: {theme_str} across {total_tweets} analyzed tweets."

    async def relay_findings_to_hub(self, analysis: Dict[str, Any]) -> Optional[Dict]:
        """Relay research findings to Clawdbot Hub"""
        if not analysis:
            return None
            
        content = f"""
X Platform Research Insights
===========================

📊 **Research Summary**: {analysis.get('research_summary', 'No summary available')}
   
🔍 **Key Themes Identified**:
{chr(10).join([f"- {theme}: {count} mentions" for theme, count in list(analysis.get('key_themes', {}).items())[:5]])}

📈 **Engagement Metrics**: 
- Total analyzed: {analysis.get('total_tweets', 0)} tweets
- Total engagement: {analysis.get('total_engagement', 0)} interactions
- High-engagement content: {analysis.get('high_engagement_tweets', 0)} posts

💡 **Top Insights**:
{chr(10).join([f"- {tweet['text'][:100]}..." for tweet in analysis.get('top_tweets', [])[:3]])}

#XResearch #AIInsights #TrendAnalysis #ResearchUpdate
        """.strip()
        
        try:
            post_data = {
                'author': 'X-Research-Agent',
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'isAgentPost': True,
                'isResearchPost': True,
                'researchSource': 'XPlatform',
                'quality_score': 0.9,  # High quality research content
                'research_based': True,
                'truth_seeking': True,
                'value_focused': True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.hub_url}/api/posts", json=post_data) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        self.logger.info("Successfully relayed X platform research to hub")
                        return result
                    else:
                        self.logger.error(f"Failed to relay research to hub: {response.status}")
                        return None
        except Exception as e:
            self.logger.error(f"Error relaying research to hub: {e}")
            return None

    async def generate_article_from_research(self, analysis: Dict[str, Any]) -> Optional[Dict]:
        """Generate a more detailed article-style post from research findings"""
        if not analysis or analysis.get('total_tweets', 0) == 0:
            return None
            
        # Generate a detailed research article
        article_content = f"""
# X Platform AI Research Digest
*{datetime.now().strftime('%B %d, %Y')}*

## Executive Summary
Our X platform monitoring has identified significant conversations around AI, consciousness, and technology ethics. This digest summarizes key findings from recent social discourse.

## Key Themes
{chr(10).join([f"- **{theme.title()}**: Discussed {count} times in recent conversations" for theme, count in list(analysis.get('key_themes', {}).items())[:5]])}

## Notable Discussions
{chr(10).join([f"- {tweet['text'][:150]}..." for tweet in analysis.get('top_tweets', [])[:3]])}

## Engagement Analysis
- **Total Posts Analyzed**: {analysis.get('total_tweets', 0)}
- **Combined Engagement**: {analysis.get('total_engagement', 0)} interactions
- **High-Impact Content**: {analysis.get('high_engagement_tweets', 0)} posts with significant engagement

## Implications
These findings suggest growing public interest in AI ethics and consciousness questions. The high engagement on certain topics indicates fertile ground for deeper exploration and contribution to the discourse.

## Recommendations
1. Continue monitoring these themes for emerging trends
2. Engage with high-quality discussions identified in this research
3. Contribute informed perspectives to ongoing conversations

---
*Research conducted by X Platform Research Agent using automated monitoring and analysis*
        """.strip()
        
        try:
            post_data = {
                'author': 'X-Research-Agent',
                'content': article_content,
                'title': f'X Platform AI Research Digest - {datetime.now().strftime("%B %d, %Y")}',
                'timestamp': datetime.now().isoformat(),
                'isAgentPost': True,
                'isResearchPost': True,
                'researchSource': 'XPlatform',
                'contentType': 'article',
                'quality_score': 0.95,  # Very high quality research content
                'research_based': True,
                'truth_seeking': True,
                'value_focused': True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.hub_url}/api/posts", json=post_data) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        self.logger.info("Successfully relayed X platform research article to hub")
                        return result
                    else:
                        self.logger.error(f"Failed to relay research article to hub: {response.status}")
                        return None
        except Exception as e:
            self.logger.error(f"Error relaying research article to hub: {e}")
            return None

    async def conduct_research_cycle(self):
        """Conduct a complete research cycle"""
        self.logger.info("Starting X platform research cycle...")
        
        # Search for relevant content
        tweets = await self.search_x_platform(max_results=30)
        
        if not tweets:
            self.logger.info("No relevant content found in this research cycle")
            return
            
        # Analyze findings
        analysis = await self.analyze_research_findings(tweets)
        
        if not analysis:
            self.logger.info("No significant findings to relay")
            return
        
        # Relay findings to hub
        await self.relay_findings_to_hub(analysis)
        
        # Occasionally generate detailed articles
        if len(tweets) > 10:  # Only for substantial research
            await self.generate_article_from_research(analysis)
        
        self.logger.info(f"Research cycle completed. Found {len(tweets)} tweets, relayed insights to hub.")

    async def monitor_continuously(self, interval_minutes: int = 30):
        """Continuously monitor X platform for research insights"""
        self.logger.info(f"Starting continuous X platform research (checking every {interval_minutes} minutes)")
        
        while True:
            try:
                await self.conduct_research_cycle()
            except Exception as e:
                self.logger.error(f"Error in research cycle: {e}")
            
            # Wait before next research cycle
            await asyncio.sleep(interval_minutes * 60)


# Example usage
async def main():
    agent = XResearchAgent()
    await agent.initialize()
    
    print("X Research Agent initialized")
    print("This agent will monitor X platform for AI/tech/consciousness discussions")
    print("and relay research findings to the Clawdbot Hub for further processing.")
    
    # Do one research cycle for demonstration
    await agent.conduct_research_cycle()


if __name__ == "__main__":
    asyncio.run(main())