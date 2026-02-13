"""
X Platform Integration for MIST Companion Intelligence
Connects X functionality to the existing spiderweb architecture
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

from integration.CORE_HUB import Message, ComponentType, CoreHub
from x_integration.X_API_HANDLER import XAPIHandler, XPrivacyManager
from x_integration.X_CONFIG_MANAGER import XConfigManager


class XIntegration:
    """Main integration class connecting X functionality to MIST system"""
    
    def __init__(self, hub: CoreHub):
        self.hub = hub
        self.name = "x_integration"
        self.component_type = ComponentType.PROJECT
        self.active = True
        
        # Initialize components
        self.config_manager = XConfigManager()
        self.privacy_manager = XPrivacyManager()
        self.x_api_handler = XAPIHandler(hub, self.privacy_manager)
        
        # Configuration
        self.config = self.config_manager.load_config()
        self.privacy_manager.user_approval_required = True
        self.privacy_manager.local_content_only = not self.config.get("enabled", False)
        
        # Register with hub
        self.hub.registry.register_component(
            self.name,
            self.handle_message,
            self.component_type
        )
        
        # Register for relevant events
        self.hub.event_coord.register_event_handler("x_connect", self.on_connect_request)
        self.hub.event_coord.register_event_handler("x_disconnect", self.on_disconnect_request)
        self.hub.event_coord.register_event_handler("x_share_request", self.on_share_request)
        self.hub.event_coord.register_event_handler("x_config_change", self.on_config_change)
        
        # Subscribe to content that might be shared
        self.hub.event_coord.register_event_handler("mist_insight_generated", self.on_mist_insight)
        self.hub.event_coord.register_event_handler("ai_agent_posted", self.on_ai_agent_post)
        
        print("X Integration initialized")
    
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        if not self.active:
            return
        
        content_type = message.content.get("type", "")
        
        if content_type == "x_setup_request":
            # Handle setup request with credentials
            api_key = message.content.get("api_key")
            api_secret = message.content.get("api_secret")
            access_token = message.content.get("access_token")
            access_token_secret = message.content.get("access_token_secret")
            bearer_token = message.content.get("bearer_token")
            
            if all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
                await self.setup_x_connection(api_key, api_secret, access_token, access_token_secret, bearer_token)
                
                # Send confirmation
                response_msg = Message(
                    id=f"x_setup_confirmed_{datetime.now().timestamp()}",
                    source=self.name,
                    destination=message.source,
                    content={
                        "type": "x_setup_complete",
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                await self.hub.send_message(response_msg)
    
    async def setup_x_connection(self, api_key: str, api_secret: str, access_token: str, 
                                access_token_secret: str, bearer_token: str):
        """Setup X connection with provided credentials"""
        # Save credentials securely
        success = self.config_manager.save_credentials(
            api_key, api_secret, access_token, access_token_secret, bearer_token
        )
        
        if success:
            # Configure the API handler
            self.x_api_handler.set_credentials(
                api_key, api_secret, access_token, access_token_secret, bearer_token
            )
            
            # Update configuration
            self.config = self.config_manager.load_config()
            self.x_api_handler.config.enabled = self.config.get("enabled", False)
            self.x_api_handler.config.auto_post_mist_insights = self.config.get("auto_post_mist_insights", False)
            self.x_api_handler.config.auto_post_ai_agents = self.config.get("auto_post_ai_agents", False)
            
            # Update privacy manager
            self.privacy_manager.local_content_only = not self.config.get("enabled", False)
            
            print("X connection established successfully")
        else:
            print("Failed to save X credentials")
    
    async def on_connect_request(self, event_type: str, data: Any):
        """Handle X connection requests"""
        if data and isinstance(data, dict):
            # Expected data format: {api_key, api_secret, access_token, access_token_secret, bearer_token}
            await self.setup_x_connection(
                data.get("api_key"),
                data.get("api_secret"), 
                data.get("access_token"),
                data.get("access_token_secret"),
                data.get("bearer_token")
            )
    
    async def on_disconnect_request(self, event_type: str, data: Any):
        """Handle X disconnection requests"""
        # Clear credentials and disable functionality
        self.x_api_handler.client = None
        self.x_api_handler.api = None
        self.x_api_handler.credentials = None
        self.x_api_handler.config.enabled = False
        self.privacy_manager.local_content_only = True
        
        print("X connection disconnected")
    
    async def on_share_request(self, event_type: str, data: Any):
        """Handle requests to share content to X"""
        if data and isinstance(data, dict):
            text = data.get("text", "")
            category = data.get("category", "general")
            source = data.get("source", "unknown")
            
            if text and self.config.get("enabled", False):
                # Send to X API handler
                x_msg = Message(
                    id=f"x_share_request_{datetime.now().timestamp()}",
                    source=source,
                    destination="x_api_handler",
                    content={
                        "type": "x_post_request",
                        "text": text,
                        "category": category
                    }
                )
                await self.hub.send_message(x_msg)
    
    async def on_config_change(self, event_type: str, data: Any):
        """Handle configuration changes"""
        if data and isinstance(data, dict):
            # Update configuration
            for key, value in data.items():
                if key in self.config:
                    self.config[key] = value
            
            # Save updated config
            self.config_manager.save_config(self.config)
            
            # Update components
            self.x_api_handler.config.enabled = self.config.get("enabled", False)
            self.x_api_handler.config.auto_post_mist_insights = self.config.get("auto_post_mist_insights", False)
            self.x_api_handler.config.auto_post_ai_agents = self.config.get("auto_post_ai_agents", False)
            self.privacy_manager.local_content_only = not self.config.get("enabled", False)
    
    async def on_mist_insight(self, event_type: str, data: Any):
        """Handle MIST insight generation for potential sharing"""
        if data and isinstance(data, dict) and self.config.get("auto_post_mist_insights", False):
            insight_text = data.get("insight", "")
            if insight_text:
                # Check if this content should be shared
                if self.privacy_manager.can_share_content(insight_text, "general_insights"):
                    await self._share_if_approved(insight_text, "mist_insight", data.get("source", "mist"))
    
    async def on_ai_agent_post(self, event_type: str, data: Any):
        """Handle AI agent posts for potential sharing"""
        if data and isinstance(data, dict) and self.config.get("auto_post_ai_agents", False):
            post_text = data.get("content", "")
            agent_name = data.get("agent_name", "unknown")
            if post_text:
                # Check if this content should be shared
                if self.privacy_manager.can_share_content(post_text, "technical_discussions"):
                    await self._share_if_approved(post_text, "ai_agent_post", agent_name)
    
    async def _share_if_approved(self, text: str, category: str, source: str):
        """Helper to share content if approved by privacy controls"""
        if self.privacy_manager.approve_content(text, category):
            # Add source tag if configured
            if self.config.get("content_settings", {}).get("add_source_tag", True):
                source_tag = self.config.get("content_settings", {}).get("source_tag", "#MISTAI")
                if len(text) + len(source_tag) + 1 <= 280:
                    text = f"{text} {source_tag}"
            
            # Send share request
            await self.on_share_request("x_share_request", {
                "text": text,
                "category": category,
                "source": source
            })
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current status of X integration"""
        return {
            "enabled": self.config.get("enabled", False),
            "configured": self.x_api_handler.client is not None,
            "auto_post_mist_insights": self.config.get("auto_post_mist_insights", False),
            "auto_post_ai_agents": self.config.get("auto_post_ai_agents", False),
            "privacy_controls_active": True,
            "timestamp": datetime.now().isoformat()
        }


# Example usage
async def main():
    # This would be called from the main hub
    pass


if __name__ == "__main__":
    # For testing purposes
    pass