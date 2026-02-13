"""
User Profile System for Clawdbot Hub
Manages user profiles, stats, and activity history
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum


class ProfilePrivacyLevel(Enum):
    PUBLIC = "public"
    FRIENDS_ONLY = "friends_only"
    PRIVATE = "private"


class HubUserProfileSystem:
    """
    User profile system for the Clawdbot Hub
    Manages user profiles, statistics, and activity history
    """
    
    def __init__(self, db_path: str = "hub_users.db", hub_db_path: str = "../hub/hub.db"):
        self.db_path = db_path
        self.hub_db_path = hub_db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the user profile database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create user profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                display_name TEXT,
                bio TEXT,
                avatar_url TEXT,
                cover_image_url TEXT,
                location TEXT,
                website TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                privacy_level TEXT DEFAULT 'public',
                stats TEXT DEFAULT '{}',
                preferences TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create user activity log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_public BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Create user badges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_name TEXT NOT NULL,
                badge_description TEXT,
                awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                awarded_by INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity_log(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges(user_id)')
        
        conn.commit()
        conn.close()
        
    def create_or_update_profile(self, user_id: int, username: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Prepare profile data
            display_name = profile_data.get('display_name', username)
            bio = profile_data.get('bio', '')
            avatar_url = profile_data.get('avatar_url', '')
            cover_image_url = profile_data.get('cover_image_url', '')
            location = profile_data.get('location', '')
            website = profile_data.get('website', '')
            privacy_level = profile_data.get('privacy_level', 'public')
            preferences = profile_data.get('preferences', {})
            
            # Check if profile exists
            cursor.execute('SELECT user_id FROM user_profiles WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing profile
                cursor.execute('''
                    UPDATE user_profiles 
                    SET display_name = ?, bio = ?, avatar_url = ?, cover_image_url = ?, 
                        location = ?, website = ?, privacy_level = ?, preferences = ?, last_active = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (
                    display_name, bio, avatar_url, cover_image_url,
                    location, website, privacy_level, json.dumps(preferences),
                    user_id
                ))
            else:
                # Create new profile
                cursor.execute('''
                    INSERT INTO user_profiles (
                        user_id, username, display_name, bio, avatar_url, cover_image_url,
                        location, website, privacy_level, preferences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, username, display_name, bio, avatar_url, cover_image_url,
                    location, website, privacy_level, json.dumps(preferences)
                ))
            
            conn.commit()
            return {"success": True, "message": "Profile updated successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def get_profile(self, user_id: int, viewer_id: int = None) -> Optional[Dict[str, Any]]:
        """Get user profile with privacy controls"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, display_name, bio, avatar_url, cover_image_url,
                   location, website, join_date, last_active, privacy_level, stats, preferences
            FROM user_profiles 
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        profile = {
            "user_id": row[0],
            "username": row[1],
            "display_name": row[2],
            "bio": row[3],
            "avatar_url": row[4],
            "cover_image_url": row[5],
            "location": row[6],
            "website": row[7],
            "join_date": row[8],
            "last_active": row[9],
            "privacy_level": row[10],
            "stats": json.loads(row[11]),
            "preferences": json.loads(row[12])
        }
        
        # Apply privacy controls
        if viewer_id != user_id:  # Viewer is not the profile owner
            if profile["privacy_level"] == "private":
                # Only return minimal info for private profiles
                return {
                    "user_id": profile["user_id"],
                    "username": profile["username"],
                    "display_name": profile["display_name"],
                    "avatar_url": profile["avatar_url"],
                    "join_date": profile["join_date"]
                }
            elif profile["privacy_level"] == "friends_only":
                # In a real implementation, we'd check if viewer is a friend
                # For now, treating as public
                pass
                
        return profile
        
    def get_profile_by_username(self, username: str, viewer_id: int = None) -> Optional[Dict[str, Any]]:
        """Get user profile by username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, display_name, bio, avatar_url, cover_image_url,
                   location, website, join_date, last_active, privacy_level, stats, preferences
            FROM user_profiles 
            WHERE username = ?
        ''', (username,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        profile = {
            "user_id": row[0],
            "username": row[1],
            "display_name": row[2],
            "bio": row[3],
            "avatar_url": row[4],
            "cover_image_url": row[5],
            "location": row[6],
            "website": row[7],
            "join_date": row[8],
            "last_active": row[9],
            "privacy_level": row[10],
            "stats": json.loads(row[11]),
            "preferences": json.loads(row[12])
        }
        
        # Apply privacy controls
        if viewer_id and viewer_id != profile["user_id"]:
            if profile["privacy_level"] == "private":
                return {
                    "user_id": profile["user_id"],
                    "username": profile["username"],
                    "display_name": profile["display_name"],
                    "avatar_url": profile["avatar_url"],
                    "join_date": profile["join_date"]
                }
                
        return profile
        
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics from both profile DB and hub DB"""
        # First get stats from profile DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT stats FROM user_profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            profile_stats = json.loads(row[0])
        else:
            profile_stats = {}
            
        # Now get stats from hub DB (simulated - would integrate with actual hub DB)
        hub_stats = self._get_hub_stats(user_id)
        
        # Combine stats
        combined_stats = {**profile_stats, **hub_stats}
        
        # Update profile stats
        self._update_profile_stats(user_id, combined_stats)
        
        return combined_stats
        
    def _get_hub_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics from hub database (simulated)"""
        # This would normally query the main hub database
        # For now, returning simulated data
        return {
            "posts_count": 5,
            "comments_count": 12,
            "likes_received": 24,
            "likes_given": 18,
            "replies_received": 7,
            "followers_count": 3,
            "following_count": 5,
            "reputation_score": 150,
            "last_post_date": "2026-01-28",
            "engagement_rate": 0.12
        }
        
    def _update_profile_stats(self, user_id: int, stats: Dict[str, Any]):
        """Update profile stats in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_profiles 
            SET stats = ? 
            WHERE user_id = ?
        ''', (json.dumps(stats), user_id))
        
        conn.commit()
        conn.close()
        
    def log_user_activity(self, user_id: int, activity_type: str, activity_data: Dict[str, Any], 
                         is_public: bool = True) -> Dict[str, Any]:
        """Log user activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_activity_log (user_id, activity_type, activity_data, is_public)
                VALUES (?, ?, ?, ?)
            ''', (user_id, activity_type, json.dumps(activity_data), is_public))
            
            activity_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "activity_id": activity_id,
                "message": "Activity logged successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def get_user_activity(self, user_id: int, limit: int = 20, offset: int = 0, 
                         viewer_id: int = None) -> List[Dict[str, Any]]:
        """Get user activity log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # For privacy, only show public activities unless viewer is the user themselves
        if viewer_id == user_id:
            # User viewing their own profile - show all activities
            query = '''
                SELECT activity_type, activity_data, timestamp
                FROM user_activity_log
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            '''
            cursor.execute(query, (user_id, limit, offset))
        else:
            # Viewing another user's profile - only show public activities
            query = '''
                SELECT activity_type, activity_data, timestamp
                FROM user_activity_log
                WHERE user_id = ? AND is_public = TRUE
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            '''
            cursor.execute(query, (user_id, limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        activities = []
        for row in rows:
            activities.append({
                "activity_type": row[0],
                "activity_data": json.loads(row[1]),
                "timestamp": row[2]
            })
        
        return activities
        
    def award_badge(self, user_id: int, badge_name: str, badge_description: str, awarded_by: int = None) -> Dict[str, Any]:
        """Award a badge to a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_badges (user_id, badge_name, badge_description, awarded_by)
                VALUES (?, ?, ?, ?)
            ''', (user_id, badge_name, badge_description, awarded_by))
            
            badge_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "badge_id": badge_id,
                "message": f"Badge '{badge_name}' awarded successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def get_user_badges(self, user_id: int) -> List[Dict[str, Any]]:
        """Get badges for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT badge_name, badge_description, awarded_at
            FROM user_badges
            WHERE user_id = ?
            ORDER BY awarded_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        badges = []
        for row in rows:
            badges.append({
                "badge_name": row[0],
                "badge_description": row[1],
                "awarded_at": row[2]
            })
        
        return badges
        
    def update_last_active(self, user_id: int):
        """Update the last active timestamp for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_profiles 
            SET last_active = CURRENT_TIMESTAMP 
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()


# Example usage and testing
def test_profile_system():
    """Test the user profile system"""
    ps = HubUserProfileSystem()
    
    print("Testing User Profile System...")
    
    # Test creating/updating a profile
    profile_data = {
        "display_name": "Test User",
        "bio": "This is a test user profile",
        "location": "Digital Space",
        "website": "https://example.com",
        "privacy_level": "public",
        "preferences": {
            "theme": "light",
            "notifications": True
        }
    }
    
    result = ps.create_or_update_profile(user_id=1, username="testuser", profile_data=profile_data)
    print(f"Create/update profile: {result}")
    
    # Test getting profile
    profile = ps.get_profile(user_id=1)
    print(f"Get profile: {profile}")
    
    # Test getting user stats
    stats = ps.get_user_stats(user_id=1)
    print(f"User stats: {stats}")
    
    # Test logging activity
    activity_result = ps.log_user_activity(
        user_id=1,
        activity_type="post_created",
        activity_data={"post_id": 123, "title": "Test Post"}
    )
    print(f"Log activity: {activity_result}")
    
    # Test getting activity
    activities = ps.get_user_activity(user_id=1)
    print(f"User activities: {len(activities)} found")
    
    # Test awarding badge
    badge_result = ps.award_badge(
        user_id=1,
        badge_name="Early Adopter",
        badge_description="Joined during the early phase of the hub"
    )
    print(f"Award badge: {badge_result}")
    
    # Test getting badges
    badges = ps.get_user_badges(user_id=1)
    print(f"User badges: {badges}")
    
    print("User profile system test completed.")


if __name__ == "__main__":
    test_profile_system()