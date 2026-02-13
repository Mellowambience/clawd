"""
X Platform Configuration Manager for MIST Companion Intelligence
Secure credential and configuration management
"""

import os
import json
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from pathlib import Path


class XConfigManager:
    """Secure configuration manager for X platform credentials"""
    
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "x_config.json"
        self.creds_file = self.config_dir / "x_credentials.enc"  # Encrypted credentials
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Generate or load encryption key
        self.key_file = self.config_dir / "x_encryption.key"
        self.cipher_suite = self._setup_encryption()
        
        # Default configuration
        self.default_config = {
            "enabled": False,
            "auto_post_mist_insights": False,
            "auto_post_ai_agents": False,
            "content_filter_enabled": True,
            "privacy_controls": {
                "personal_information": False,
                "private_thoughts": False,
                "daily_routine": False,
                "general_insights": True,
                "technical_discussions": True
            },
            "rate_limiting": {
                "posts_per_hour": 5,
                "posts_per_day": 50,
                "minimum_interval_minutes": 1
            },
            "content_settings": {
                "max_length": 280,
                "truncate_long_posts": True,
                "add_source_tag": True,
                "source_tag": "#MISTAI"
            }
        }
    
    def _setup_encryption(self) -> Fernet:
        """Setup encryption for credential storage"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as key_file:
                key = key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(key)
        
        return Fernet(key)
    
    def save_credentials(self, api_key: str, api_secret: str, access_token: str, 
                        access_token_secret: str, bearer_token: str) -> bool:
        """Securely save X API credentials"""
        try:
            credentials = {
                "api_key": api_key,
                "api_secret": api_secret,
                "access_token": access_token,
                "access_token_secret": access_token_secret,
                "bearer_token": bearer_token,
                "timestamp": str(self._get_timestamp())
            }
            
            # Encrypt credentials
            encrypted_data = self.cipher_suite.encrypt(json.dumps(credentials).encode())
            
            # Save to encrypted file
            with open(self.creds_file, 'wb') as file:
                file.write(encrypted_data)
            
            print("X credentials saved securely")
            return True
            
        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False
    
    def load_credentials(self) -> Optional[Dict[str, str]]:
        """Load and decrypt X API credentials"""
        if not self.creds_file.exists():
            print("No X credentials file found")
            return None
        
        try:
            with open(self.creds_file, 'rb') as file:
                encrypted_data = file.read()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            
            return credentials
            
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration settings"""
        try:
            with open(self.config_file, 'w') as file:
                json.dump(config, file, indent=2)
            
            print("X configuration saved")
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration settings"""
        if not self.config_file.exists():
            # Save default config and return it
            self.save_config(self.default_config)
            return self.default_config.copy()
        
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
            
            # Merge with defaults to ensure all keys exist
            merged_config = self.default_config.copy()
            self._deep_merge(merged_config, config)
            
            return merged_config
            
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()
    
    def _deep_merge(self, base_dict: Dict, update_dict: Dict):
        """Deep merge two dictionaries"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_credentials(self, creds: Dict[str, str]) -> bool:
        """Validate that all required credentials are present"""
        required_fields = [
            'api_key', 'api_secret', 
            'access_token', 'access_token_secret', 
            'bearer_token'
        ]
        
        for field in required_fields:
            if not creds.get(field):
                print(f"Missing required credential: {field}")
                return False
        
        return True
    
    def get_public_config(self) -> Dict[str, Any]:
        """Get configuration without sensitive data"""
        config = self.load_config()
        
        # Remove any potentially sensitive keys from public config
        public_config = config.copy()
        
        return public_config


# Example usage and setup
def setup_x_integration(api_key: str, api_secret: str, access_token: str, 
                       access_token_secret: str, bearer_token: str) -> bool:
    """
    Helper function to setup X integration with credentials
    """
    config_manager = XConfigManager()
    
    # Save credentials securely
    if not config_manager.save_credentials(
        api_key, api_secret, access_token, access_token_secret, bearer_token
    ):
        print("Failed to save X credentials")
        return False
    
    # Load and display public config
    public_config = config_manager.get_public_config()
    print("X integration configured successfully")
    print(f"Configuration: {json.dumps(public_config, indent=2)}")
    
    return True


if __name__ == "__main__":
    # Example usage:
    # setup_x_integration("your_api_key", "your_api_secret", "your_access_token", 
    #                    "your_access_token_secret", "your_bearer_token")
    pass