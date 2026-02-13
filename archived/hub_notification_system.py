"""
Notification System for Clawdbot Hub
Implements real-time alerts for replies, likes, and other activities
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import threading
from enum import Enum


class NotificationType(Enum):
    LIKE = "like"
    COMMENT = "comment"
    REPLY = "reply"
    MENTION = "mention"
    FOLLOW = "follow"
    SYSTEM = "system"


class HubNotificationSystem:
    """
    Notification system for the Clawdbot Hub
    Handles real-time alerts for user activities
    """
    
    def __init__(self, db_path: str = "hub_notifications.db", hub_db_path: str = "../hub/hub.db"):
        self.db_path = db_path
        self.hub_db_path = hub_db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the notification database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                related_object_type TEXT,
                related_object_id INTEGER,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                extra_data TEXT DEFAULT '{}'
            )
        ''')
        
        # Create index for user_id for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)')
        
        conn.commit()
        conn.close()
        
    def create_notification(self, user_id: int, ntype: NotificationType, title: str, message: str, 
                          related_object_type: str = None, related_object_id: int = None, 
                          extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new notification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO notifications (
                    user_id, type, title, message, 
                    related_object_type, related_object_id, extra_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, ntype.value, title, message,
                related_object_type, related_object_id,
                json.dumps(extra_data or {})
            ))
            
            notification_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "notification_id": notification_id,
                "message": "Notification created successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def get_user_notifications(self, user_id: int, limit: int = 50, offset: int = 0, 
                             unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, type, title, message, related_object_type, related_object_id, 
                   is_read, created_at, extra_data
            FROM notifications
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if unread_only:
            query += ' AND is_read = FALSE'
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        notifications = []
        for row in rows:
            notifications.append({
                "id": row[0],
                "type": row[1],
                "title": row[2],
                "message": row[3],
                "related_object_type": row[4],
                "related_object_id": row[5],
                "is_read": row[6],
                "created_at": row[7],
                "extra_data": json.loads(row[8])
            })
        
        return notifications
        
    def mark_as_read(self, notification_ids: List[int], user_id: int = None) -> Dict[str, Any]:
        """Mark notifications as read"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if user_id:
                # Only mark as read if notifications belong to the user
                placeholders = ','.join(['?' for _ in notification_ids])
                query = f'''
                    UPDATE notifications 
                    SET is_read = TRUE 
                    WHERE id IN ({placeholders}) AND user_id = ?
                '''
                params = notification_ids + [user_id]
            else:
                # Mark any notifications as read (admin function)
                placeholders = ','.join(['?' for _ in notification_ids])
                query = f'UPDATE notifications SET is_read = TRUE WHERE id IN ({placeholders})'
                params = notification_ids
            
            cursor.execute(query, params)
            updated_count = cursor.rowcount
            conn.commit()
            
            return {
                "success": True,
                "updated_count": updated_count,
                "message": f"Marked {updated_count} notifications as read"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def mark_all_as_read(self, user_id: int) -> Dict[str, Any]:
        """Mark all notifications for a user as read"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE notifications 
                SET is_read = TRUE 
                WHERE user_id = ? AND is_read = FALSE
            ''', (user_id,))
            
            updated_count = cursor.rowcount
            conn.commit()
            
            return {
                "success": True,
                "updated_count": updated_count,
                "message": f"Marked all {updated_count} notifications as read"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) 
            FROM notifications 
            WHERE user_id = ? AND is_read = FALSE
        ''', (user_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
        
    def cleanup_old_notifications(self, days_old: int = 30) -> Dict[str, Any]:
        """Remove notifications older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        try:
            cursor.execute('''
                DELETE FROM notifications 
                WHERE created_at < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Deleted {deleted_count} old notifications"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def notify_like(self, post_author_id: int, liker_username: str, post_title: str, post_id: int) -> Dict[str, Any]:
        """Notify a user that their post was liked"""
        if post_author_id is None:
            return {"success": False, "error": "Post author ID is required"}
            
        title = f"New Like on Your Post"
        message = f"{liker_username} liked your post '{post_title[:50]}{'...' if len(post_title) > 50 else ''}'"
        
        return self.create_notification(
            user_id=post_author_id,
            ntype=NotificationType.LIKE,
            title=title,
            message=message,
            related_object_type="post",
            related_object_id=post_id,
            extra_data={
                "liker_username": liker_username,
                "post_title": post_title
            }
        )
        
    def notify_comment(self, post_author_id: int, commenter_username: str, comment_content: str, 
                      post_title: str, post_id: int, comment_id: int) -> Dict[str, Any]:
        """Notify a user that their post received a comment"""
        title = f"New Comment on Your Post"
        message = f"{commenter_username} commented on your post '{post_title[:30]}{'...' if len(post_title) > 30 else ''}'"
        
        return self.create_notification(
            user_id=post_author_id,
            ntype=NotificationType.COMMENT,
            title=title,
            message=message,
            related_object_type="comment",
            related_object_id=comment_id,
            extra_data={
                "commenter_username": commenter_username,
                "comment_content": comment_content,
                "post_title": post_title,
                "post_id": post_id
            }
        )
        
    def notify_reply(self, original_poster_id: int, replier_username: str, reply_content: str, 
                    original_content: str, reply_id: int) -> Dict[str, Any]:
        """Notify a user that someone replied to their comment"""
        title = f"New Reply to Your Comment"
        message = f"{replier_username} replied to your comment"
        
        return self.create_notification(
            user_id=original_poster_id,
            ntype=NotificationType.REPLY,
            title=title,
            message=message,
            related_object_type="reply",
            related_object_id=reply_id,
            extra_data={
                "replier_username": replier_username,
                "reply_content": reply_content,
                "original_content": original_content
            }
        )
        
    def notify_mention(self, mentioned_user_id: int, mentioner_username: str, content_snippet: str, 
                      object_type: str, object_id: int) -> Dict[str, Any]:
        """Notify a user that they were mentioned"""
        title = f"You Were Mentioned"
        message = f"{mentioner_username} mentioned you in a {object_type}"
        
        return self.create_notification(
            user_id=mentioned_user_id,
            ntype=NotificationType.MENTION,
            title=title,
            message=message,
            related_object_type=object_type,
            related_object_id=object_id,
            extra_data={
                "mentioner_username": mentioner_username,
                "content_snippet": content_snippet,
                "object_type": object_type
            }
        )
        
    def notify_follow(self, followed_user_id: int, follower_username: str) -> Dict[str, Any]:
        """Notify a user that they gained a follower"""
        title = f"New Follower"
        message = f"{follower_username} started following you"
        
        return self.create_notification(
            user_id=followed_user_id,
            ntype=NotificationType.FOLLOW,
            title=title,
            message=message,
            related_object_type="user",
            related_object_id=None,
            extra_data={
                "follower_username": follower_username
            }
        )


# Example usage and testing
def test_notification_system():
    """Test the notification system"""
    ns = HubNotificationSystem()
    
    print("Testing Notification System...")
    
    # Test creating a notification
    result = ns.create_notification(
        user_id=1,
        ntype=NotificationType.LIKE,
        title="Test Notification",
        message="This is a test notification",
        extra_data={"test": True}
    )
    print(f"Create notification: {result}")
    
    # Test getting notifications
    notifications = ns.get_user_notifications(user_id=1)
    print(f"User notifications: {len(notifications)} found")
    
    # Test unread count
    unread_count = ns.get_unread_count(user_id=1)
    print(f"Unread count: {unread_count}")
    
    # Test marking as read
    if notifications:
        result = ns.mark_as_read([notifications[0]['id']], user_id=1)
        print(f"Mark as read: {result}")
    
    print("Notification system test completed.")


if __name__ == "__main__":
    test_notification_system()