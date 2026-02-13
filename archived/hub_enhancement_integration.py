"""
Comprehensive Integration of Hub Enhancements
Brings together authentication, notifications, profiles, search, and admin features
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List
from hub_auth_system import HubAuthSystem
from hub_notification_system import HubNotificationSystem, NotificationType
from hub_user_profiles import HubUserProfileSystem
from hub_search_discovery import HubSearchDiscoverySystem
from hub_admin_dashboard import AdminDashboard, ModerationAction


class HubEnhancementIntegration:
    """
    Integrates all hub enhancements into a cohesive system
    """
    
    def __init__(self):
        self.auth_system = HubAuthSystem()
        self.notification_system = HubNotificationSystem()
        self.profile_system = HubUserProfileSystem()
        self.search_system = HubSearchDiscoverySystem()
        self.admin_dashboard = AdminDashboard()
        
    def register_user_with_profile(self, username: str, email: str, password: str, 
                                 profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a user and create their profile in one step
        """
        # Register user via auth system
        auth_result = self.auth_system.register_user(username, email, password)
        
        if not auth_result["success"]:
            return auth_result
        
        user_id = auth_result["user_id"]
        
        # Create profile for the user
        profile_result = self.profile_system.create_or_update_profile(
            user_id=user_id,
            username=username,
            profile_data=profile_data
        )
        
        if not profile_result["success"]:
            return profile_result
        
        # Log the activity
        self.profile_system.log_user_activity(
            user_id=user_id,
            activity_type="account_created",
            activity_data={"username": username, "email": email}
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "message": "User registered and profile created successfully"
        }
        
    def authenticate_and_notify(self, username_or_email: str, password: str, 
                              ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """
        Authenticate user and handle associated notifications
        """
        # Login via auth system
        auth_result = self.auth_system.login_user(
            username_or_email, password, ip_address, user_agent
        )
        
        if not auth_result["success"]:
            return auth_result
        
        user_id = auth_result["user_id"]
        
        # Update last active in profile
        self.profile_system.update_last_active(user_id)
        
        # Log login activity
        self.profile_system.log_user_activity(
            user_id=user_id,
            activity_type="login",
            activity_data={"ip_address": ip_address, "user_agent": user_agent}
        )
        
        # Get any unread notifications for the user
        unread_count = self.notification_system.get_unread_count(user_id)
        
        auth_result["unread_notifications"] = unread_count
        auth_result["profile"] = self.profile_system.get_profile(user_id, user_id)
        
        return auth_result
        
    def create_post_with_indexing(self, user_id: int, title: str, content: str, 
                                tags: List[str] = None) -> Dict[str, Any]:
        """
        Create a post and index it for search
        """
        # This would normally interact with the main hub database
        # For this example, we'll simulate creating a post and indexing it
        
        # Log the activity
        self.profile_system.log_user_activity(
            user_id=user_id,
            activity_type="post_created",
            activity_data={"title": title, "tags": tags or []}
        )
        
        # Index the content for search
        index_result = self.search_system.index_content(
            object_type="post",
            object_id=999,  # Simulated post ID
            title=title,
            content=content,
            author=self.auth_system.get_user_by_id(user_id)["username"],
            tags=tags
        )
        
        # Award badge for first post if applicable
        stats = self.profile_system.get_user_stats(user_id)
        if stats.get("posts_count", 0) <= 1:
            self.profile_system.award_badge(
                user_id=user_id,
                badge_name="First Post",
                badge_description="Created their first post on the hub"
            )
        
        return {
            "success": True,
            "message": "Post created and indexed successfully",
            "index_result": index_result
        }
        
    def handle_like_notification(self, post_author_id: int, liker_user_id: str, 
                               post_title: str, post_id: int) -> Dict[str, Any]:
        """
        Handle notification when a post is liked
        """
        liker_username = self.auth_system.get_user_by_id(liker_user_id)["username"]
        
        return self.notification_system.notify_like(
            post_author_id=post_author_id,
            liker_username=liker_username,
            post_title=post_title,
            post_id=post_id
        )
        
    def handle_comment_notification(self, post_author_id: int, commenter_user_id: int,
                                  comment_content: str, post_title: str, 
                                  post_id: int, comment_id: int) -> Dict[str, Any]:
        """
        Handle notification when a post receives a comment
        """
        commenter_username = self.auth_system.get_user_by_id(commenter_user_id)["username"]
        
        return self.notification_system.notify_comment(
            post_author_id=post_author_id,
            commenter_username=commenter_username,
            comment_content=comment_content,
            post_title=post_title,
            post_id=post_id,
            comment_id=comment_id
        )
        
    def get_enhanced_user_profile(self, user_id: int, viewer_id: int = None) -> Dict[str, Any]:
        """
        Get a user profile with additional enhancements
        """
        profile = self.profile_system.get_profile(user_id, viewer_id)
        
        if not profile:
            return {"success": False, "error": "Profile not found"}
        
        # Add stats
        stats = self.profile_system.get_user_stats(user_id)
        
        # Add badges
        badges = self.profile_system.get_user_badges(user_id)
        
        # Add recent activity (last 5 activities)
        recent_activities = self.profile_system.get_user_activity(user_id, limit=5, viewer_id=viewer_id)
        
        enhanced_profile = {
            **profile,
            "stats": stats,
            "badges": badges,
            "recent_activity": recent_activities
        }
        
        return {
            "success": True,
            "profile": enhanced_profile
        }
        
    def search_with_enhancements(self, query: str, user_id: int = None, 
                               limit: int = 20) -> Dict[str, Any]:
        """
        Enhanced search with additional features
        """
        # Perform the search
        search_result = self.search_system.search(query, user_id, limit)
        
        if not search_result["success"]:
            return search_result
        
        # Add trending topics to the results
        trending_topics = self.search_system.get_trending_topics(limit=5)
        
        # Add popular content to the results
        popular_content = self.search_system.get_popular_content(limit=5)
        
        enhanced_result = {
            **search_result,
            "trending_topics": trending_topics,
            "popular_content": popular_content,
            "suggestions": self.search_system.get_suggested_searches(query.split()[0] if query.split() else "", 5)
        }
        
        return enhanced_result
        
    def get_admin_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive admin dashboard data
        """
        # Get summary data
        summary = self.admin_dashboard.get_dashboard_summary()
        
        # Get additional metrics
        total_users = len([self.auth_system.get_user_by_id(uid) for uid in range(1, 1000)])  # Simplified
        total_posts = 50  # Simulated
        total_comments = 120  # Simulated
        
        # Get trending topics
        trending = self.search_system.get_trending_topics()
        
        # Get recent activities
        recent_activities = self.get_recent_platform_activities(limit=10)
        
        admin_data = {
            **summary,
            "total_users": total_users,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "trending_topics": trending,
            "recent_activities": recent_activities
        }
        
        return admin_data
        
    def get_recent_platform_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent activities across the platform
        """
        # This would normally aggregate data from multiple sources
        # For now, returning simulated data
        return [
            {"type": "user_joined", "username": "newuser123", "time": "2026-02-01T16:30:00Z"},
            {"type": "post_created", "author": "testuser", "title": "AI Ethics Discussion", "time": "2026-02-01T16:25:00Z"},
            {"type": "comment_added", "author": "anotheruser", "post_title": "Consciousness Explained", "time": "2026-02-01T16:20:00Z"},
        ][:limit]
        
    def moderate_content(self, moderator_id: int, action: ModerationAction, 
                        target_type: str, target_id: int, reason: str = "") -> Dict[str, Any]:
        """
        Handle content moderation with all associated actions
        """
        # Take moderation action
        mod_result = self.admin_dashboard.take_moderation_action(
            moderator_id, action, target_type, target_id, reason
        )
        
        if not mod_result["success"]:
            return mod_result
        
        # Update search index if content was removed
        if action == ModerationAction.REMOVE:
            # Mark as inactive in search index
            conn = sqlite3.connect(self.search_system.search_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE search_index 
                SET is_active = FALSE 
                WHERE object_type = ? AND object_id = ?
            ''', (target_type, target_id))
            conn.commit()
            conn.close()
        
        # Log additional activity
        self.profile_system.log_user_activity(
            user_id=moderator_id,
            activity_type="moderation_action",
            activity_data={
                "action": action.value,
                "target_type": target_type,
                "target_id": target_id,
                "reason": reason
            }
        )
        
        return mod_result


# Example usage and testing
def test_enhancement_integration():
    """Test the integrated enhancement system"""
    ie = HubEnhancementIntegration()
    
    print("Testing Hub Enhancement Integration...")
    
    # Test user registration with profile
    profile_data = {
        "display_name": "Enhanced User",
        "bio": "A user enjoying the enhanced hub experience",
        "location": "Digital Realm",
        "website": "https://enhanced-hub.example.com",
        "privacy_level": "public"
    }
    
    result = ie.register_user_with_profile(
        username="enhanced_user",
        email="enhanced@example.com",
        password="securepassword123",
        profile_data=profile_data
    )
    print(f"Register user with profile: {result}")
    
    # Test authentication
    auth_result = ie.authenticate_and_notify(
        "enhanced_user", "securepassword123"
    )
    print(f"Authenticate user: {auth_result}")
    
    if auth_result["success"]:
        user_id = auth_result["user_id"]
        
        # Test creating a post with indexing
        post_result = ie.create_post_with_indexing(
            user_id=user_id,
            title="My First Enhanced Post",
            content="This post benefits from the enhanced hub features including search indexing and notifications.",
            tags=["enhancement", "hub", "first-post"]
        )
        print(f"Create post with indexing: {post_result}")
        
        # Test getting enhanced profile
        profile_result = ie.get_enhanced_user_profile(user_id, user_id)
        print(f"Enhanced profile: {profile_result['success']}")
        
        # Test enhanced search
        search_result = ie.search_with_enhancements("hub enhancement")
        print(f"Enhanced search results: {len(search_result.get('results', []))} found")
    
    # Test admin dashboard data
    admin_data = ie.get_admin_dashboard_data()
    print(f"Admin dashboard data retrieved: {bool(admin_data)}")
    
    print("Hub enhancement integration test completed.")


if __name__ == "__main__":
    test_enhancement_integration()