#!/usr/bin/env python3
"""
Configuration for Multi-AI Collaboration System
Integrates with existing Moltbot tools and settings
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class MultiAIConfig:
    """Configuration class for the multi-AI collaboration system"""
    
    def __init__(self):
        self.config_path = Path.home() / ".clawdbot" / "multi_ai_config.json"
        self.default_config = {
            "enabled": True,
            "max_collaborators": 4,
            "default_timeout": 30,
            "enable_logging": True,
            "log_level": "INFO",
            "collaboration_strategies": {
                "sequential": {
                    "name": "Sequential",
                    "description": "AIs contribute in sequence, each building on the previous contribution",
                    "enabled": True
                },
                "parallel": {
                    "name": "Parallel",
                    "description": "AIs work simultaneously on different aspects, then synthesize",
                    "enabled": False  # Advanced feature for later
                },
                "round_robin": {
                    "name": "Round Robin",
                    "description": "AIs take turns refining the solution iteratively",
                    "enabled": True
                }
            },
            "model_preferences": {
                "primary": "moonshot/moonshot-v1-128k",
                "secondary": [
                    "moonshot/moonshot-v1-32k",
                    "moonshot/moonshot-v1-8k",
                    "google-genai/gemini-2.0-flash",
                    "qwen-portal/coder-model",
                    "xai-portal/grok-4",
                    "ollama/llama3.3"
                ]
            },
            "task_routing": {
                "coding_tasks": ["qwen-portal/coder-model", "moonshot/moonshot-v1-128k"],
                "analytical_tasks": ["xai-portal/grok-4", "moonshot/moonshot-v1-128k"],
                "creative_tasks": ["moonshot/moonshot-v1-128k", "google-genai/gemini-2.0-flash"],
                "research_tasks": ["xai-portal/grok-4", "moonshot/moonshot-v1-128k"]
            },
            "performance_metrics": {
                "track_response_times": True,
                "track_collaboration_effectiveness": True,
                "enable_profiling": True
            },
            "integration_settings": {
                "enable_with_existing_tools": True,
                "tool_access_level": "standard",  # Can be "standard", "elevated", "full"
                "memory_sharing": True,
                "context_preservation": True
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default if not exists"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_config = self.deep_merge(self.default_config, loaded_config)
                    return merged_config
            except Exception as e:
                print(f"Warning: Could not load config file, using defaults: {e}")
                return self.default_config
        else:
            # Create config directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            # Create default config file
            self.save_config(self.default_config)
            return self.default_config
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_model_priority_list(self) -> List[str]:
        """Get the ordered list of models to use for collaboration"""
        primary = self.config["model_preferences"]["primary"]
        secondary = self.config["model_preferences"]["secondary"]
        
        return [primary] + [model for model in secondary if model != primary]
    
    def get_models_for_task_type(self, task_type: str) -> List[str]:
        """Get models preferred for a specific task type"""
        if task_type in self.config["task_routing"]:
            return self.config["task_routing"][task_type]
        else:
            # Return default model list if task type not specified
            return self.get_model_priority_list()
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        try:
            self.config = self.deep_merge(self.config, updates)
            return self.save_config()
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def enable_collaboration(self) -> bool:
        """Enable the multi-AI collaboration system"""
        return self.update_config({"enabled": True})
    
    def disable_collaboration(self) -> bool:
        """Disable the multi-AI collaboration system"""
        return self.update_config({"enabled": False})
    
    def set_primary_model(self, model_id: str) -> bool:
        """Set a new primary model for collaboration"""
        return self.update_config({
            "model_preferences": {
                "primary": model_id
            }
        })


class MultiAIIntegrationManager:
    """Manages integration between multi-AI system and existing Moltbot tools"""
    
    def __init__(self):
        self.config = MultiAIConfig()
        self.active = self.config.config["enabled"]
    
    def initialize_collaboration_tools(self) -> Dict[str, Any]:
        """Initialize tools for multi-AI collaboration"""
        tools = {
            "multi_ai_collaborate": {
                "description": "Execute a multi-AI collaboration for complex tasks",
                "parameters": {
                    "task": {"type": "string", "description": "The task to collaborate on"},
                    "strategy": {"type": "string", "description": "Collaboration strategy to use", "default": "sequential"},
                    "max_collaborators": {"type": "integer", "description": "Maximum number of AIs to involve", "default": 3}
                }
            },
            "multi_ai_analyze": {
                "description": "Analyze a task to determine optimal collaboration approach",
                "parameters": {
                    "task": {"type": "string", "description": "The task to analyze"}
                }
            },
            "multi_ai_status": {
                "description": "Get status of the multi-AI collaboration system",
                "parameters": {}
            },
            "multi_ai_insights": {
                "description": "Get insights and metrics from past collaborations",
                "parameters": {}
            }
        }
        
        return tools
    
    def get_tool_functions(self) -> Dict[str, callable]:
        """Get actual functions that implement the tools"""
        from integrated_multi_ai import IntegratedMultiAICollaborator
        
        async def multi_ai_collaborate(task: str, strategy: str = "sequential", max_collaborators: int = 3):
            """Execute a multi-AI collaboration"""
            if not self.active:
                return {"error": "Multi-AI collaboration is not enabled"}
            
            collaborator = IntegratedMultiAICollaborator()
            result = await collaborator.execute_smart_collaboration(task)
            return result
        
        async def multi_ai_analyze(task: str):
            """Analyze a task for optimal collaboration"""
            if not self.active:
                return {"error": "Multi-AI collaboration is not enabled"}
            
            collaborator = IntegratedMultiAICollaborator()
            analysis = collaborator._analyze_task_requirements(task)
            return analysis
        
        def multi_ai_status():
            """Get status of the multi-AI system"""
            return {
                "enabled": self.active,
                "configuration_loaded": True,
                "primary_model": self.config.config["model_preferences"]["primary"],
                "available_strategies": [k for k, v in self.config.config["collaboration_strategies"].items() if v["enabled"]],
                "total_collaborators": len(self.config.get_model_priority_list())
            }
        
        def multi_ai_insights():
            """Get insights from past collaborations"""
            if not self.active:
                return {"error": "Multi-AI collaboration is not enabled"}
            
            # This would normally access historical data
            # For now, return a template
            return {
                "collaboration_count": 0,  # Placeholder
                "average_collaborators_per_task": 0,  # Placeholder
                "most_effective_strategies": [],  # Placeholder
                "performance_metrics_available": self.config.config["performance_metrics"]["track_response_times"]
            }
        
        return {
            "multi_ai_collaborate": multi_ai_collaborate,
            "multi_ai_analyze": multi_ai_analyze,
            "multi_ai_status": multi_ai_status,
            "multi_ai_insights": multi_ai_insights
        }
    
    def enable_system(self) -> bool:
        """Enable the multi-AI collaboration system"""
        success = self.config.enable_collaboration()
        if success:
            self.active = True
        return success
    
    def disable_system(self) -> bool:
        """Disable the multi-AI collaboration system"""
        success = self.config.disable_collaboration()
        if success:
            self.active = False
        return success


# Function to install the multi-AI collaboration system
def install_multi_ai_collaboration():
    """Install and configure the multi-AI collaboration system"""
    print("[INSTALL] Installing Multi-AI Collaboration System...")
    
    # Create the integration manager
    manager = MultiAIIntegrationManager()
    
    # Enable the system
    if manager.enable_system():
        print("[SUCCESS] Multi-AI Collaboration System enabled")
    else:
        print("[ERROR] Failed to enable Multi-AI Collaboration System")
        return False
    
    # Save the configuration
    config = MultiAIConfig()
    if config.save_config():
        print("[SUCCESS] Configuration saved")
    else:
        print("[ERROR] Failed to save configuration")
        return False
    
    # Display current status
    status = manager.get_tool_functions()["multi_ai_status"]()
    print(f"[STATUS] Current status: {status}")
    
    print("[COMPLETE] Multi-AI Collaboration System installed and ready!")
    print("   - Use multi_ai_collaborate() for complex tasks")
    print("   - Use multi_ai_analyze() to analyze tasks")
    print("   - Use multi_ai_status() to check system status")
    print("   - Use multi_ai_insights() to get performance metrics")
    
    return True


if __name__ == "__main__":
    # Install the multi-AI collaboration system
    success = install_multi_ai_collaboration()
    
    if success:
        print("\nThe multi-AI collaboration system is now integrated with your existing setup!")
        print("   It will work alongside your current tools and can be called upon for complex tasks.")
    else:
        print("\nInstallation failed. Please check the logs above.")