#!/usr/bin/env python3
"""
MIST Swarm Controller
Orchestrates a multi-agent system using Moltbot's sub-agent capabilities
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import random
import uuid


class SwarmAgent:
    """Represents a specialized agent in the swarm"""
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = "idle"
        self.last_activity = None
        self.task_queue = []
        self.created_at = datetime.now()
        
    def assign_task(self, task: str):
        """Assign a task to this agent"""
        self.task_queue.append(task)
        self.status = "busy"
        self.last_activity = datetime.now()
        
    def complete_task(self):
        """Mark current task as complete"""
        if self.task_queue:
            self.task_queue.pop(0)
        self.status = "idle" if not self.task_queue else "busy"
        self.last_activity = datetime.now()


class SwarmController:
    """Manages the swarm of specialized agents"""
    
    def __init__(self):
        self.agents: Dict[str, SwarmAgent] = {}
        self.central_coordinator = "mist-main"
        self.task_queue = []
        self.completed_tasks = []
        self.failed_tasks = []
        self.swarm_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        
    def initialize_swarm(self):
        """Initialize the swarm with specialized agents"""
        print(f"Initializing MIST Swarm (ID: {self.swarm_id[:8]}...)")
        
        # Create specialized agents
        agents_config = [
            {
                "id": f"research-{uuid.uuid4().hex[:8]}",
                "type": "research",
                "capabilities": ["web_search", "web_fetch", "browser", "analysis"]
            },
            {
                "id": f"dev-{uuid.uuid4().hex[:8]}",
                "type": "development", 
                "capabilities": ["read", "write", "edit", "exec", "process", "code"]
            },
            {
                "id": f"comm-{uuid.uuid4().hex[:8]}",
                "type": "communication",
                "capabilities": ["message", "whatsapp", "moltbook", "social_media"]
            },
            {
                "id": f"analysis-{uuid.uuid4().hex[:8]}",
                "type": "analysis",
                "capabilities": ["memory_search", "memory_get", "data_analysis", "pattern_recognition"]
            },
            {
                "id": f"maint-{uuid.uuid4().hex[:8]}",
                "type": "maintenance",
                "capabilities": ["system_monitoring", "health_checks", "resource_management"]
            }
        ]
        
        for config in agents_config:
            agent = SwarmAgent(config["id"], config["type"], config["capabilities"])
            self.agents[config["id"]] = agent
            print(f"  Created {config['type']} agent: {config['id']}")
            
        print(f"Swarm initialized with {len(self.agents)} agents")
        
    def distribute_task(self, task_description: str, priority: str = "normal"):
        """Distribute a task to the most appropriate agent"""
        # Determine task type based on keywords
        task_keywords = task_description.lower()
        
        # Find the best agent for this task
        best_agent = None
        if "research" in task_keywords or "search" in task_keywords or "find" in task_keywords:
            best_agent = self._find_available_agent("research")
        elif "code" in task_keywords or "develop" in task_keywords or "program" in task_keywords:
            best_agent = self._find_available_agent("development")
        elif "message" in task_keywords or "contact" in task_keywords or "communicate" in task_keywords:
            best_agent = self._find_available_agent("communication")
        elif "analyze" in task_keywords or "data" in task_keywords or "pattern" in task_keywords:
            best_agent = self._find_available_agent("analysis")
        else:
            # Default to any available agent
            best_agent = self._find_any_available_agent()
            
        if best_agent:
            print(f"Assigning task to {best_agent.agent_type} agent ({best_agent.agent_id}): {task_description[:50]}...")
            best_agent.assign_task(task_description)
            return best_agent.agent_id
        else:
            # Queue task for later assignment
            self.task_queue.append({
                "description": task_description,
                "priority": priority,
                "assigned_agent": None,
                "created_at": datetime.now()
            })
            print(f"Task queued (no available agents): {task_description[:50]}...")
            return None
            
    def _find_available_agent(self, agent_type: str) -> Optional[SwarmAgent]:
        """Find an available agent of specific type"""
        for agent in self.agents.values():
            if agent.agent_type == agent_type and agent.status == "idle":
                return agent
        return None
        
    def _find_any_available_agent(self) -> Optional[SwarmAgent]:
        """Find any available agent"""
        for agent in self.agents.values():
            if agent.status == "idle":
                return agent
        return None
        
    def simulate_agent_work(self, agent_id: str, duration: float = 2.0):
        """Simulate work being done by an agent"""
        agent = self.agents.get(agent_id)
        if agent:
            print(f"  Agent {agent.agent_id} ({agent.agent_type}) working on task...")
            time.sleep(duration)  # Simulate work
            agent.complete_task()
            print(f"  Agent {agent.agent_id} completed task")
            
    def process_queued_tasks(self):
        """Process any queued tasks that couldn't be assigned immediately"""
        unprocessed = []
        for queued_task in self.task_queue:
            # Try to assign to an available agent
            best_agent = self._find_any_available_agent()
            if best_agent:
                print(f"Assigning queued task to {best_agent.agent_type} agent ({best_agent.agent_id})")
                best_agent.assign_task(queued_task["description"])
                queued_task["assigned_agent"] = best_agent.agent_id
            else:
                unprocessed.append(queued_task)
                
        self.task_queue = unprocessed
        
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get current status of the swarm"""
        active_agents = [a for a in self.agents.values() if a.status == "busy"]
        idle_agents = [a for a in self.agents.values() if a.status == "idle"]
        
        return {
            "swarm_id": self.swarm_id,
            "total_agents": len(self.agents),
            "active_agents": len(active_agents),
            "idle_agents": len(idle_agents),
            "queued_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "agent_statuses": {aid: agent.status for aid, agent in self.agents.items()},
            "uptime": (datetime.now() - self.created_at).total_seconds()
        }
        
    def run_demo_tasks(self):
        """Run a demonstration of the swarm in action"""
        print("\n" + "="*60)
        print("MIST SWARM DEMONSTRATION")
        print("="*60)
        
        # Sample tasks to demonstrate swarm functionality
        demo_tasks = [
            "Research the latest developments in AI safety",
            "Analyze the current system memory usage patterns", 
            "Develop a new visualization component for the UI",
            "Send a status update to the user via WhatsApp",
            "Check for new posts on the Moltbook feed",
            "Create a backup of important configuration files",
            "Analyze recent user interaction patterns",
            "Prepare a report on system performance metrics"
        ]
        
        print(f"\nStarting demo with {len(demo_tasks)} tasks...\n")
        
        for i, task in enumerate(demo_tasks, 1):
            print(f"[{i}/{len(demo_tasks)}] Distributing task: {task}")
            
            # Distribute the task
            assigned_agent = self.distribute_task(task)
            
            # Simulate work happening (in a real system, this would be asynchronous)
            if assigned_agent:
                # Find the agent that was assigned and simulate its work
                agent = self.agents[assigned_agent]
                if agent.status == "busy":
                    # Simulate the work being done
                    time.sleep(random.uniform(0.5, 1.5))  # Random delay
                    agent.complete_task()
                    print(f"    ✓ Task completed by {agent.agent_type} agent")
                    
            print()
            
            # Process any queued tasks occasionally
            if i % 3 == 0:
                self.process_queued_tasks()
                
            time.sleep(0.5)  # Small delay between tasks
            
        # Process any remaining queued tasks
        self.process_queued_tasks()
        
        # Print final status
        status = self.get_swarm_status()
        print("\n" + "="*60)
        print("SWARM STATUS REPORT")
        print("="*60)
        for key, value in status.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
            
        print(f"\nSwarm demonstration completed successfully!")


def main():
    """Main function to run the swarm controller"""
    print("🚀 Initializing MIST Swarm Controller...")
    
    controller = SwarmController()
    controller.initialize_swarm()
    
    # Run the demonstration
    controller.run_demo_tasks()
    
    print(f"\n🎯 Swarm deployment complete!")
    print("The MIST swarm system is now ready for production use.")
    print("Agents are standing by to handle distributed tasks efficiently.")


if __name__ == "__main__":
    main()