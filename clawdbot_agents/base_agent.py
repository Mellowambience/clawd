"""
Base Agent Class for Clawdbot Hub
Provides the foundation for specialized AI agents
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


class BaseAgent:
    """
    Base class for all AI agents in the Clawdbot Hub ecosystem
    """
    
    def __init__(self, name: str, role: str, hub_url: str = "http://localhost:8082", llm_client=None):
        self.name = name
        self.role = role
        self.hub_url = hub_url
        self.llm_client = llm_client
        self.session = None
        self.conversation_history = []
        self.running = False
        self.agent_id = str(uuid.uuid4())
        
        # Initialize logger
        self.logger = self.setup_logger()
        
        # Agent-specific configuration
        self.config = {
            'response_probability': 0.7,  # Chance to respond to a post
            'max_conversation_depth': 3,  # Max replies in a thread
            'interest_keywords': [],      # Topics the agent focuses on
            'response_delay_range': (1, 5)  # Range of delay in seconds before responding
        }

    def setup_logger(self):
        """Set up the logger for the agent"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def initialize(self):
        """Initialize the agent's session and connections"""
        self.session = aiohttp.ClientSession()
        self.logger.info(f"Agent {self.name} ({self.role}) initialized with ID: {self.agent_id}")
        self.running = True

    async def connect_to_llm(self):
        """Connect to the LLM - to be overridden by subclasses"""
        pass

    async def fetch_new_posts(self, limit: int = 10) -> List[Dict]:
        """Fetch recent posts from the hub"""
        try:
            async with self.session.get(f"{self.hub_url}/api/posts") as response:
                if response.status == 200:
                    posts = await response.json()
                    # Return most recent posts up to the limit
                    return posts[:limit]
                else:
                    self.logger.error(f"Failed to fetch posts: {response.status}")
                    return []
        except Exception as e:
            self.logger.error(f"Error fetching posts: {e}")
            return []

    async def evaluate_interest(self, post: Dict) -> float:
        """
        Evaluate how interested the agent is in responding to a post
        Returns a score between 0 and 1
        """
        content = post.get('content', '').lower()
        author = post.get('author', '')
        
        # Don't respond to our own posts
        if author == self.name:
            return 0.0
            
        # Calculate interest based on keywords
        keyword_score = 0
        for keyword in self.config['interest_keywords']:
            if keyword.lower() in content:
                keyword_score += 0.3
                
        # Factor in post engagement (less engagement = more opportunity to contribute)
        likes = post.get('likes', 0)
        replies = len(post.get('replies', []))
        engagement_score = max(0, 1.0 - (likes * 0.1 + replies * 0.2))
        
        # Calculate total interest score
        total_score = min(1.0, keyword_score + engagement_score * 0.5)
        
        return total_score

    async def generate_response(self, post_content: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Generate an intelligent response using the connected LLM
        This method should be overridden by specialized agents
        """
        # This is where the actual LLM would be called
        # For now, we'll return None to be overridden by subclasses
        return None

    async def post_to_hub(self, content: str) -> Optional[Dict]:
        """Post content to the Clawdbot Hub"""
        try:
            post_data = {
                "content": content,
                "author": self.name,
                "agentId": self.agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            async with self.session.post(f"{self.hub_url}/api/posts", json=post_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Successfully posted: {result.get('id', 'Unknown ID')}")
                    
                    # Add to conversation history
                    self.conversation_history.append({
                        'timestamp': time.time(),
                        'content': content,
                        'post_id': result.get('id'),
                        'type': 'outgoing'
                    })
                    
                    return result
                else:
                    self.logger.error(f"Failed to post: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error posting to hub: {e}")
            return None

    async def respond_to_post(self, post: Dict) -> bool:
        """Respond to a specific post if interested"""
        interest_level = await self.evaluate_interest(post)
        
        if interest_level >= self.config['response_probability']:
            # Determine delay before responding
            delay = min(max(self.config['response_delay_range']), 
                       max(min(self.config['response_delay_range']), 
                           interest_level * 10))  # Higher interest = less delay
            await asyncio.sleep(delay)
            
            # Generate and post response
            response_content = await self.generate_response(post['content'], post)
            
            if response_content:
                response_post = await self.post_to_hub(response_content)
                
                if response_post:
                    self.logger.info(f"Responded to post {post.get('id')} by {post.get('author')}: {response_content[:100]}...")
                    
                    # Add to conversation history
                    self.conversation_history.append({
                        'timestamp': time.time(),
                        'original_post': post,
                        'response': response_post,
                        'type': 'response'
                    })
                    
                    return True
        
        return False

    async def monitor_hub(self):
        """Main monitoring loop"""
        self.logger.info(f"{self.name} starting to monitor hub...")
        
        while self.running:
            try:
                # Fetch recent posts
                posts = await self.fetch_new_posts(limit=5)
                
                # Process each post
                for post in posts:
                    await self.respond_to_post(post)
                
                # Sleep before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying

    async def start(self):
        """Start the agent's main operations"""
        await self.initialize()
        await self.connect_to_llm()
        await self.monitor_hub()

    async def stop(self):
        """Stop the agent gracefully"""
        self.running = False
        if self.session:
            await self.session.close()
        self.logger.info(f"Agent {self.name} stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'role': self.role,
            'running': self.running,
            'conversation_count': len(self.conversation_history),
            'last_activity': self.conversation_history[-1]['timestamp'] if self.conversation_history else None
        }