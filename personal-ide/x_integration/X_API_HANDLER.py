"""
X Platform API Handler for MIST Companion Intelligence
Securely manages X/Twitter API integration with privacy controls
"""

import asyncio
import os
import tweepy
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

from integration.CORE_HUB import Message, ComponentType, CoreHub


@dataclass
class XCredentials:
    """X API Credentials with secure handling"""
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    bearer_token: str


@dataclass
class PostConfig:
    """Configuration for X posts"""
    enabled: bool = False
    auto_post_mist_insights: bool = False
    auto_post_ai_agents: bool = False
    content_filter_enabled: bool = True
    privacy_controls: Dict[str, bool] = field(default_factory=dict)


class XPrivacyManager:
    """Manages privacy controls for X integration"""
    
    def __init__(self):
        self.enabled_categories = set()
        self.disabled_categories = set()
        self.user_approval_required = True
        self.local_content_only = False
    
    def can_share_content(self, content: str, category: str = "general") -> bool:
        """Check if content can be shared to X"""
        if self.local_content_only:
            return False
        
        if category in self.disabled_categories:
            return False
        
        if self.enabled_categories and category not in self.enabled_categories:
            return False
        
        # Basic content checks
        if len(content) > 280:  # X character limit
            return False
        
        return True
    
    def approve_content(self, content: str, category: str = "general") -> bool:
        """Get approval for content sharing (if required)"""
        if not self.user_approval_required:
            return self.can_share_content(content, category)
        
        # In a real implementation, this would prompt the user
        # For now, we'll assume approved content that passes other checks
        return self.can_share_content(content, category)


class XAPIHandler:
    """Main handler for X platform API operations"""
    
    def __init__(self, hub: CoreHub, privacy_manager: XPrivacyManager = None):
        self.hub = hub
        self.privacy_manager = privacy_manager or XPrivacyManager()
        self.credentials: Optional[XCredentials] = None
        self.client: Optional[Any] = None
        self.api: Optional[Any] = None
        self.active = True
        self.name = "x_api_handler"
        self.component_type = ComponentType.PROJECT  # Using PROJECT type as it's external integration
        
        # Post configuration
        self.config = PostConfig()
        
        # Rate limiting and tracking
        self.post_count_today = 0
        self.last_post_time = None
        self.rate_limit_remaining = 50  # X API v2 has 50 posts per day
        
        # Register with hub
        self.hub.registry.register_component(
            self.name,
            self.handle_message,
            self.component_type
        )
        
        # Register for relevant events
        self.hub.event_coord.register_event_handler("x_post_request", self.on_post_request)
        self.hub.event_coord.register_event_handler("x_config_update", self.on_config_update)
        self.hub.event_coord.register_event_handler("x_credentials_set", self.on_credentials_set)
    
    def set_credentials(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str, bearer_token: str):
        """Securely set X API credentials"""
        self.credentials = XCredentials(
            api_key=api_key,
            api_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            bearer_token=bearer_token
        )
        
        # Initialize tweepy client
        try:
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            
            # Initialize legacy API for additional functionality
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(auth)
            
            print("X API credentials set successfully")
            
            # Trigger event to notify other components
            asyncio.create_task(
                self.hub.trigger_event("x_credentials_set", {
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                })
            )
            
        except Exception as e:
            print(f"Error initializing X API: {e}")
            self.client = None
            self.api = None
    
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        if not self.active:
            return
        
        content_type = message.content.get("type", "")
        
        if content_type == "x_post_request":
            text = message.content.get("text", "")
            category = message.content.get("category", "general")
            await self.post_to_x(text, category, message.source)
        
        elif content_type == "x_config_request":
            # Return current configuration
            config_msg = Message(
                id=f"{message.id}_response",
                source=self.name,
                destination=message.source,
                content={
                    "type": "x_config_response",
                    "config": {
                        "enabled": self.config.enabled,
                        "auto_post_mist_insights": self.config.auto_post_mist_insights,
                        "auto_post_ai_agents": self.config.auto_post_ai_agents,
                        "content_filter_enabled": self.config.content_filter_enabled
                    }
                },
                context={"response_to": message.id}
            )
            await self.hub.send_message(config_msg)
    
    async def post_to_x(self, text: str, category: str = "general", requester: str = "unknown"):
        """Post content to X platform with privacy controls"""
        if not self.config.enabled:
            print("X posting is disabled in configuration")
            return False
        
        if not self.client:
            print("X API not properly configured - no credentials set")
            return False
        
        if not self.privacy_manager.can_share_content(text, category):
            print(f"Content blocked by privacy manager: {category}")
            return False
        
        if not self.privacy_manager.approve_content(text, category):
            print(f"Content not approved for sharing: {category}")
            return False
        
        # Check rate limits
        if self.post_count_today >= 50:
            print("Daily post limit reached")
            return False
        
        if self.last_post_time:
            # Basic rate limiting - minimum 1 minute between posts
            time_since_last = datetime.now() - self.last_post_time
            if time_since_last.total_seconds() < 60:
                print("Rate limit - waiting before next post")
                return False
        
        try:
            # Post to X
            response = self.client.create_tweet(text=text)
            
            if response.data and 'id' in response.data:
                tweet_id = response.data['id']
                
                # Update tracking
                self.post_count_today += 1
                self.last_post_time = datetime.now()
                
                # Send confirmation
                confirmation_msg = Message(
                    id=f"x_post_success_{tweet_id}",
                    source=self.name,
                    destination=requester,
                    content={
                        "type": "x_post_success",
                        "tweet_id": tweet_id,
                        "text": text,
                        "category": category,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                await self.hub.send_message(confirmation_msg)
                
                print(f"Successfully posted to X: {text[:50]}...")
                return True
            else:
                print(f"Failed to post to X: {response}")
                return False
                
        except Exception as e:
            print(f"Error posting to X: {e}")
            # Send failure notification
            error_msg = Message(
                id=f"x_post_error_{datetime.now().timestamp()}",
                source=self.name,
                destination=requester,
                content={
                    "type": "x_post_error",
                    "error": str(e),
                    "text": text,
                    "category": category,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.hub.send_message(error_msg)
            return False
    
    def can_post_now(self) -> bool:
        """Check if we can post now based on rate limits"""
        if self.post_count_today >= 50:
            return False
        
        if self.last_post_time:
            time_since_last = datetime.now() - self.last_post_time
            return time_since_last.total_seconds() >= 60
        
        return True
    
    def reset_daily_limits(self):
        """Reset daily posting limits"""
        self.post_count_today = 0
        # Reset at start of each day
    
    async def on_post_request(self, event_type: str, data: Any):
        """Handle X post requests"""
        if data and isinstance(data, dict):
            text = data.get("text", "")
            category = data.get("category", "general")
            requester = data.get("requester", "unknown")
            
            if text:
                await self.post_to_x(text, category, requester)
    
    async def on_config_update(self, event_type: str, data: Any):
        """Handle configuration updates"""
        if data and isinstance(data, dict):
            for key, value in data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
    
    async def on_credentials_set(self, event_type: str, data: Any):
        """Handle credential setting events"""
        if data and isinstance(data, dict):
            if all(k in data for k in ['api_key', 'api_secret', 'access_token', 'access_token_secret', 'bearer_token']):
                self.set_credentials(
                    data['api_key'],
                    data['api_secret'],
                    data['access_token'],
                    data['access_token_secret'],
                    data['bearer_token']
                )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of X integration"""
        return {
            "configured": self.client is not None,
            "enabled": self.config.enabled,
            "post_count_today": self.post_count_today,
            "rate_limit_remaining": max(0, 50 - self.post_count_today),
            "last_post_time": self.last_post_time.isoformat() if self.last_post_time else None,
            "can_post_now": self.can_post_now(),
            "privacy_controls_active": True
        }


# Example usage
async def main():
    # This would be called from the main hub
    pass


if __name__ == "__main__":
    # For testing purposes
    pass