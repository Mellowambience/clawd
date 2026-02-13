"""
Admin Dashboard for Clawdbot Hub
Provides tools to moderate content and manage agents
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum


class ModerationAction(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    FLAG = "flag"
    REMOVE = "remove"
    WARN_USER = "warn_user"
    SUSPEND_USER = "suspend_user"
    BAN_USER = "ban_user"


class AdminDashboard:
    """
    Admin dashboard for the Clawdbot Hub
    Provides tools to moderate content and manage agents
    """
    
    def __init__(self, hub_db_path: str = "../hub/hub.db", admin_db_path: str = "hub_admin.db"):
        self.hub_db_path = hub_db_path
        self.admin_db_path = admin_db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the admin database"""
        conn = sqlite3.connect(self.admin_db_path)
        cursor = conn.cursor()
        
        # Create moderation logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moderation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moderator_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                target_type TEXT NOT NULL,  -- 'post', 'comment', 'user', 'agent'
                target_id INTEGER NOT NULL,
                reason TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create reported content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reported_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_user_id INTEGER NOT NULL,
                target_type TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',  -- 'pending', 'reviewed', 'resolved'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                reviewer_id INTEGER
            )
        ''')
        
        # Create agent management table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_management (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                agent_type TEXT NOT NULL,  -- 'philosopher', 'technologist', etc.
                status TEXT DEFAULT 'active',  -- 'active', 'paused', 'disabled'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                activity_log TEXT DEFAULT '[]',
                config_overrides TEXT DEFAULT '{}'
            )
        ''')
        
        # Create admin users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                role TEXT DEFAULT 'moderator',  -- 'moderator', 'admin', 'super_admin'
                permissions TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create analytics snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_users INTEGER DEFAULT 0,
                total_posts INTEGER DEFAULT 0,
                total_comments INTEGER DEFAULT 0,
                active_users_today INTEGER DEFAULT 0,
                flagged_content_count INTEGER DEFAULT 0,
                resolved_reports_count INTEGER DEFAULT 0,
                agent_activity_count INTEGER DEFAULT 0,
                data JSON
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_moderation_logs_moderator ON moderation_logs(moderator_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_moderation_logs_target ON moderation_logs(target_type, target_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reported_content_status ON reported_content(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reported_content_target ON reported_content(target_type, target_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_management_status ON agent_management(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_admin_users_role ON admin_users(role)')
        
        conn.commit()
        conn.close()
        
    def log_moderation_action(self, moderator_id: int, action: ModerationAction, target_type: str, 
                            target_id: int, reason: str = "", notes: str = "") -> Dict[str, Any]:
        """Log a moderation action"""
        conn = sqlite3.connect(self.admin_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO moderation_logs (
                    moderator_id, action, target_type, target_id, reason, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (moderator_id, action.value, target_type, target_id, reason, notes))
            
            log_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "log_id": log_id,
                "message": "Moderation action logged successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def report_content(self, reporter_user_id: int, target_type: str, target_id: int, 
                      reason: str, description: str = "") -> Dict[str, Any]:
        """Report content for review"""
        conn = sqlite3.connect(self.admin_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO reported_content (
                    reporter_user_id, target_type, target_id, reason, description
                ) VALUES (?, ?, ?, ?, ?)
            ''', (reporter_user_id, target_type, target_id, reason, description))
            
            report_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "report_id": report_id,
                "message": "Content reported successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def get_pending_reports(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get pending reports that need review"""
        conn = sqlite3.connect(self.admin_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, reporter_user_id, target_type, target_id, reason, description, created_at
            FROM reported_content
            WHERE status = 'pending'
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        reports = []
        for row in rows:
            reports.append({
                "id": row[0],
                "reporter_user_id": row[1],
                "target_type": row[2],
                "target_id": row[3],
                "reason": row[4],
                "description": row[5],
                "created_at": row[6]
            })
        
        return reports
        
    def update_report_status(self, report_id: int, status: str, reviewer_id: int = None) -> Dict[str, Any]:
        """Update the status of a report"""
        conn = sqlite3.connect(self.admin_db_path)
        cursor = conn.cursor()
        
        try:
            update_fields = ["status = ?"]
            params = [status]
            
            if reviewer_id:
                update_fields.append("reviewed_at = CURRENT_TIMESTAMP")
                update_fields.append("reviewer_id = ?")
                params.extend([reviewer_id])
            
            query = f"UPDATE reported_content SET {', '.join(update_fields)} WHERE id = ?"
            params.append(report_id)
            
            cursor.execute(query, params)
            
            if cursor.rowcount > 0:
                conn.commit()
                return {"success": True, "message": f"Report status updated to {status}"}
            else:
                return {"success": False, "error": "Report not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def get_moderation_logs(self, limit: int = 50, offset: int = 0, 
                           moderator_id: int = None) -> List[Dict[str, Any]]:
        """Get moderation logs"""
        conn = sqlite3.connect(self.admin_db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, moderator_id, action, target_type, target_id, reason, notes, created_at
            FROM moderation_logs
        '''
        params = []
        
        if moderator_id:
            query += ' WHERE moderator_id = ?'
            params.append(moderator_id)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append({
                "id": row[0],
                "moderator_id": row[1],
                "action": row[2],
                "target_type": row[3],
                "target_id": row[4],
                "reason": row[5],
                "notes": row[6],
                "created_at": row[7]
            })
        
        return logs
        
    def get_content_details(self, target_type: str, target_id: int) -> Optional[Dict[str, Any]]:
        """Get details about reported content from the main hub DB"""
        # This would normally query the main hub database
        # For now, returning simulated data
        conn = sqlite3.connect(self.hub_db_path)
        cursor = conn.cursor()
        
        try:
            if target_type == "post":
                cursor.execute('SELECT * FROM posts WHERE id = ?', (target_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "type": "post",
                        "id": row[0],
                        "title": row[1],
                        "content": row[2],
                        "author": row[3],
                        "created_at": row[4],
                        "likes": row[5],
                        "comments_count": row[6]
                    }
            elif target_type == "comment":
                cursor.execute('SELECT * FROM comments WHERE id = ?', (target_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "type": "comment",
                        "id": row[0],
                        "content": row[1],
                        "author": row[2],
                        "post_id": row[3],
                        "created_at": row[4]
                    }
            elif target_type == "user":
                # This would query the users table in the hub DB
                pass
        except:
            pass
        finally:
            conn.close()
        
        return None
        
    def manage_agent(self, agent_name: str, action: str, reason: str = "") -> Dict[str, Any]:
        """Manage an AI agent (activate, pause, disable)"""
        conn = sqlite3.connect(self.admin_db_path)
        cursor = conn.cursor()
        
        try:
            # First, check if agent exists
            cursor.execute('SELECT id, status FROM agent_management WHERE agent_name = ?', (agent_name,))
            result = cursor.fetchone()
            
            if not result:
                return {"success": False, "error": "Agent not found"}
            
            agent_id, current_status = result
            
            if action == "activate":
                new_status = "active"
            elif action == "pause":
                new_status = "paused"
            elif action == "disable":
                new_status = "disabled"
            else:
                return {"success": False, "error": "Invalid action"}
            
            cursor.execute('''
                UPDATE agent_management 
                SET status = ?, last_active = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_status, agent_id))
            
            # Log the action
            cursor.execute('''
                INSERT INTO moderation_logs (
                    moderator_id, action, target_type, target_id, reason, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (0, f"agent_{action}", "agent", agent_id, reason, f"Agent {agent_name} {action}d"))
            
            conn.commit()
            return {
                "success": True,
                "message": f"Agent {agent_name} {action}d successfully",
                "new_status": new_status
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        conn = sqlite3.connect(self.admin_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT agent_name, agent_type, status, created_at, last_active
            FROM agent_management
            ORDER BY last_active DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        agents = []
        for row in rows:
            agents.append({
                "name": row[0],
                "type": row[1],
                "status": row[2],
                "created_at": row[3],
                "last_active": row[4]
            })
        
        return agents
        
    def get_platform_analytics(self, days_back: int = 30) -> Dict[str, Any]:
        """Get platform analytics"""
        conn = sqlite3.connect(self.admin_db_path)
        cursor = conn.cursor()
        
        # Get the most recent analytics snapshot
        cursor.execute('''
            SELECT snapshot_date, total_users, total_posts, total_comments, 
                   active_users_today, flagged_content_count, resolved_reports_count,
                   agent_activity_count, data
            FROM analytics_snapshots
            ORDER BY snapshot_date DESC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "snapshot_date": row[0],
                "total_users": row[1],
                "total_posts": row[2],
                "total_comments": row[3],
                "active_users_today": row[4],
                "flagged_content_count": row[5],
                "resolved_reports_count": row[6],
                "agent_activity_count": row[7],
                "additional_data": json.loads(row[8]) if row[8] else {}
            }
        else:
            # Return empty analytics if no snapshot exists
            return {
                "snapshot_date": datetime.now().isoformat(),
                "total_users": 0,
                "total_posts": 0,
                "total_comments": 0,
                "active_users_today": 0,
                "flagged_content_count": 0,
                "resolved_reports_count": 0,
                "agent_activity_count": 0,
                "additional_data": {}
            }
            
    def take_moderation_action(self, moderator_id: int, action: ModerationAction, target_type: str, 
                              target_id: int, reason: str = "", notes: str = "") -> Dict[str, Any]:
        """Take a moderation action and update the main hub DB accordingly"""
        # Log the action
        log_result = self.log_moderation_action(moderator_id, action, target_type, target_id, reason, notes)
        
        if not log_result["success"]:
            return log_result
        
        # Perform the action on the main hub DB
        conn = sqlite3.connect(self.hub_db_path)
        cursor = conn.cursor()
        
        try:
            if action == ModerationAction.REMOVE and target_type == "post":
                # Remove the post
                cursor.execute('UPDATE posts SET is_deleted = 1 WHERE id = ?', (target_id,))
            elif action == ModerationAction.REMOVE and target_type == "comment":
                # Remove the comment
                cursor.execute('UPDATE comments SET is_deleted = 1 WHERE id = ?', (target_id,))
            elif action == ModerationAction.FLAG:
                # Flag the content (set a flag field)
                table_name = "posts" if target_type == "post" else "comments"
                cursor.execute(f'UPDATE {table_name} SET flagged = 1 WHERE id = ?', (target_id,))
            
            conn.commit()
            return {
                "success": True,
                "message": f"Moderation action '{action.value}' taken on {target_type} {target_id}",
                "log_id": log_result["log_id"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
            
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get a summary for the admin dashboard"""
        # Get pending reports
        pending_reports = len(self.get_pending_reports(limit=100))
        
        # Get agent statuses
        agents = self.get_agent_status()
        active_agents = len([a for a in agents if a["status"] == "active"])
        
        # Get platform analytics
        analytics = self.get_platform_analytics()
        
        # Get recent moderation actions
        recent_actions = self.get_moderation_logs(limit=10)
        
        return {
            "pending_reports": pending_reports,
            "total_agents": len(agents),
            "active_agents": active_agents,
            "platform_analytics": analytics,
            "recent_moderation_actions": recent_actions[:5],  # Last 5 actions
            "dashboard_refresh_time": datetime.now().isoformat()
        }


# Example usage and testing
def test_admin_dashboard():
    """Test the admin dashboard system"""
    ad = AdminDashboard()
    
    print("Testing Admin Dashboard System...")
    
    # Test logging a moderation action
    result = ad.log_moderation_action(
        moderator_id=1,
        action=ModerationAction.FLAG,
        target_type="post",
        target_id=123,
        reason="Potential spam content",
        notes="Needs review by senior moderator"
    )
    print(f"Log moderation action: {result}")
    
    # Test reporting content
    result = ad.report_content(
        reporter_user_id=2,
        target_type="post",
        target_id=123,
        reason="spam",
        description="This post appears to be promotional spam"
    )
    print(f"Report content: {result}")
    
    # Test getting pending reports
    pending_reports = ad.get_pending_reports()
    print(f"Pending reports: {len(pending_reports)} found")
    
    # Test agent management
    # First, add a test agent to the database
    conn = sqlite3.connect(ad.admin_db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO agent_management (agent_name, agent_type, status)
        VALUES ('Test-Agent', 'philosopher', 'active')
    ''')
    conn.commit()
    conn.close()
    
    # Now test managing the agent
    result = ad.manage_agent("Test-Agent", "pause", "Scheduled maintenance")
    print(f"Manage agent: {result}")
    
    # Test getting agent status
    agents = ad.get_agent_status()
    print(f"Agent statuses: {len(agents)} agents found")
    
    # Test dashboard summary
    summary = ad.get_dashboard_summary()
    print(f"Dashboard summary: {summary}")
    
    print("Admin dashboard system test completed.")


if __name__ == "__main__":
    test_admin_dashboard()