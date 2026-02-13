"""
Authentication System for Clawdbot Hub
Implements secure login, registration, and session management
"""

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import re


class HubAuthSystem:
    """
    Authentication system for the Clawdbot Hub
    Handles user registration, login, and session management
    """
    
    def __init__(self, db_path: str = "hub_auth.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the authentication database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                profile_data TEXT DEFAULT '{}'
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token)')
        
        conn.commit()
        conn.close()
        
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash a password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Combine password and salt, then hash
        pwd_hash = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'), 
                                      salt.encode('utf-8'), 
                                      100000)
        return pwd_hash.hex(), salt
        
    def validate_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Validate a password against stored hash"""
        pwd_hash, _ = self.hash_password(password, salt)
        return pwd_hash == stored_hash
        
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    def validate_username(self, username: str) -> bool:
        """Validate username format (alphanumeric and underscores only, 3-20 chars)"""
        if len(username) < 3 or len(username) > 20:
            return False
        return re.match(r'^[a-zA-Z0-9_]+$', username) is not None
        
    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        # Validate inputs
        if not self.validate_username(username):
            return {"success": False, "error": "Username must be 3-20 alphanumeric characters or underscores"}
        
        if not self.validate_email(email):
            return {"success": False, "error": "Invalid email format"}
        
        if len(password) < 8:
            return {"success": False, "error": "Password must be at least 8 characters"}
        
        # Hash password
        pwd_hash, salt = self.hash_password(password)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt)
                VALUES (?, ?, ?, ?)
            ''', (username, email, pwd_hash, salt))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True, 
                "user_id": user_id,
                "message": "User registered successfully"
            }
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return {"success": False, "error": "Username already exists"}
            elif "email" in str(e):
                return {"success": False, "error": "Email already exists"}
            else:
                return {"success": False, "error": "Registration failed"}
        finally:
            conn.close()
            
    def login_user(self, username_or_email: str, password: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Authenticate user and create session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Try to find user by username or email
        cursor.execute('''
            SELECT id, password_hash, salt FROM users 
            WHERE username = ? OR email = ?
        ''', (username_or_email, username_or_email))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return {"success": False, "error": "Invalid credentials"}
        
        user_id, stored_hash, salt = result
        
        # Verify password
        if not self.validate_password(password, stored_hash, salt):
            conn.close()
            return {"success": False, "error": "Invalid credentials"}
        
        # Create session token
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=7)  # Session expires in 7 days
        
        # Insert session
        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_token, expires_at, ip_address, user_agent))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "user_id": user_id,
            "message": "Login successful"
        }
        
    def logout_user(self, session_token: str) -> Dict[str, Any]:
        """Logout user by invalidating session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
        affected_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if affected_rows > 0:
            return {"success": True, "message": "Logged out successfully"}
        else:
            return {"success": False, "error": "Invalid session token"}
            
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token and return user info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.user_id, u.username, u.email, u.is_admin, u.profile_data, s.expires_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ? AND s.expires_at > ?
        ''', (session_token, datetime.now()))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "user_id": result[0],
                "username": result[1],
                "email": result[2],
                "is_admin": result[3],
                "profile_data": json.loads(result[4]),
                "expires_at": result[5]
            }
        return None
        
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, created_at, is_active, is_admin, profile_data
            FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "username": result[1],
                "email": result[2],
                "created_at": result[3],
                "is_active": result[4],
                "is_admin": result[5],
                "profile_data": json.loads(result[6])
            }
        return None
        
    def update_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET profile_data = ? WHERE id = ?
            ''', (json.dumps(profile_data), user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {"success": True, "message": "Profile updated successfully"}
            else:
                conn.close()
                return {"success": False, "error": "User not found"}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e)}
            
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics (would integrate with hub data)"""
        # This would typically integrate with the main hub database
        # For now, returning placeholder data
        return {
            "posts_count": 0,
            "likes_received": 0,
            "comments_made": 0,
            "join_date": "2026-02-01",
            "reputation_score": 100
        }


# Example usage and testing
def test_auth_system():
    """Test the authentication system"""
    auth = HubAuthSystem()
    
    print("Testing Authentication System...")
    
    # Test registration
    result = auth.register_user("testuser", "test@example.com", "securepassword123")
    print(f"Registration: {result}")
    
    # Test login
    result = auth.login_user("testuser", "securepassword123")
    print(f"Login: {result}")
    
    if result["success"]:
        session_token = result["session_token"]
        
        # Test session validation
        user_info = auth.validate_session(session_token)
        print(f"Session validation: {user_info}")
        
        # Test logout
        result = auth.logout_user(session_token)
        print(f"Logout: {result}")
    
    print("Authentication system test completed.")


if __name__ == "__main__":
    test_auth_system()