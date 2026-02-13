#!/usr/bin/env python3
"""
Integrated Multi-AI Collaboration System
Connects the collaboration engine with Moltbot's existing tool framework
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from multi_ai_collaboration import MultiAICollaborationEngine, AITaskType
import sys
import os

# Add the current directory to the path so we can import other modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class IntegratedMultiAICollaborator:
    """
    An integrated system that combines the multi-AI collaboration engine
    with Moltbot's existing tools and capabilities
    """
    
    def __init__(self):
        self.engine = MultiAICollaborationEngine()
        self.session_log = []
        self.active_collaborations = {}
    
    def log_session(self, action: str, details: Dict[str, Any]):
        """Log collaboration sessions for tracking and debugging"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "session_id": str(uuid.uuid4())
        }
        self.session_log.append(log_entry)
        
        # Print to console for immediate feedback
        print(f"[LOG] {action}: {details}")
    
    async def execute_smart_collaboration(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a smart collaboration that can adapt based on the task and context
        """
        self.log_session("COLLABORATION_START", {
            "task": task,
            "context_available": context is not None,
            "timestamp": datetime.now().isoformat()
        })
        
        # Determine if this task requires special handling
        task_analysis = self._analyze_task_requirements(task)
        
        # Adjust collaboration parameters based on task complexity
        max_collaborators = min(
            task_analysis.get("recommended_collaborators", 3),
            len(self.engine.collaborators)
        )
        
        # Execute the collaboration
        result = await self.engine.execute_collaboration(task, max_collaborators)
        
        # Format the result for integration with other systems
        formatted_result = {
            "task_id": result.task_id,
            "collaboration_result": result.final_result,
            "contributions": result.contributions,
            "execution_order": result.execution_order,
            "metrics": result.metrics,
            "task_analysis": task_analysis,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
        self.log_session("COLLABORATION_COMPLETE", {
            "task_id": result.task_id,
            "collaborators_used": len(result.contributions),
            "execution_time": result.metrics.get("estimated_completion_time")
        })
        
        return formatted_result
    
    def _analyze_task_requirements(self, task: str) -> Dict[str, Any]:
        """Analyze a task to determine optimal collaboration parameters"""
        task_lower = task.lower()
        
        # Analyze task complexity and requirements
        analysis = {
            "complexity": "medium",  # low, medium, high, extreme
            "requires_vision": False,
            "requires_coding": False,
            "requires_analysis": False,
            "requires_reasoning": False,
            "requires_research": False,
            "requires_writing": False,
            "recommended_collaborators": 3,
            "special_requirements": []
        }
        
        # Complexity indicators
        if len(task) > 500:
            analysis["complexity"] = "high"
            analysis["recommended_collaborators"] = 4
        elif len(task) > 200:
            analysis["complexity"] = "medium"
        else:
            analysis["complexity"] = "low"
            analysis["recommended_collaborators"] = 2
        
        # Task type indicators
        if any(word in task_lower for word in ['image', 'visual', 'picture', 'vision', 'photo']):
            analysis["requires_vision"] = True
            analysis["special_requirements"].append("vision_model_required")
        
        if any(word in task_lower for word in ['code', 'program', 'function', 'script', 'develop', 'implement']):
            analysis["requires_coding"] = True
            analysis["special_requirements"].append("coding_model_preferred")
        
        if any(word in task_lower for word in ['analyze', 'analysis', 'compare', 'review', 'examine']):
            analysis["requires_analysis"] = True
            analysis["special_requirements"].append("analysis_model_preferred")
        
        if any(word in task_lower for word in ['reason', 'think', 'logical', 'solve', 'problem']):
            analysis["requires_reasoning"] = True
            analysis["special_requirements"].append("reasoning_model_preferred")
        
        if any(word in task_lower for word in ['research', 'find', 'investigate', 'study', 'explore']):
            analysis["requires_research"] = True
            analysis["special_requirements"].append("research_model_preferred")
        
        if any(word in task_lower for word in ['write', 'draft', 'compose', 'document', 'create']):
            analysis["requires_writing"] = True
            analysis["special_requirements"].append("writing_model_preferred")
        
        return analysis
    
    async def execute_adaptive_collaboration(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute collaboration with adaptive parameters based on task analysis
        """
        # Analyze the task to determine optimal approach
        analysis = self._analyze_task_requirements(task)
        
        # Adjust collaborators based on requirements
        required_specialties = []
        if analysis["requires_coding"]:
            required_specialties.append(AITaskType.CODING)
        if analysis["requires_analysis"]:
            required_specialties.append(AITaskType.ANALYSIS)
        if analysis["requires_reasoning"]:
            required_specialties.append(AITaskType.REASONING)
        if analysis["requires_research"]:
            required_specialties.append(AITaskType.RESEARCH)
        if analysis["requires_writing"]:
            required_specialties.append(AITaskType.WRITING)
        if analysis["requires_vision"]:
            required_specialties.append(AITaskType.VISION)
        
        # If specific specialties are required, prioritize AIs with those specialties
        if required_specialties:
            # This would require modifying the collaboration engine to accept specialty preferences
            # For now, we'll proceed with the standard approach but note the requirements
            print(f"[INFO] Task requires specialties: {required_specialties}")
        
        # Execute the collaboration
        return await self.execute_smart_collaboration(task, context)
    
    def get_collaboration_insights(self) -> Dict[str, Any]:
        """Get insights from past collaborations"""
        if not self.session_log:
            return {"message": "No collaborations performed yet"}
        
        # Count different types of collaborations
        collaboration_starts = [entry for entry in self.session_log if entry["action"] == "COLLABORATION_START"]
        collaboration_completes = [entry for entry in self.session_log if entry["action"] == "COLLABORATION_COMPLETE"]
        
        insights = {
            "total_sessions": len(self.session_log),
            "total_collaborations_started": len(collaboration_starts),
            "total_collaborations_completed": len(collaboration_completes),
            "completion_rate": len(collaboration_completes) / len(collaboration_starts) if collaboration_starts else 0,
            "most_common_tasks": self._get_most_common_tasks(collaboration_starts),
            "recent_activity": self.session_log[-5:]  # Last 5 entries
        }
        
        return insights
    
    def _get_most_common_tasks(self, starts: List[Dict]) -> List[str]:
        """Extract most common task types from session logs"""
        tasks = [entry["details"]["task"] for entry in starts]
        # Simple approach: return first few tasks as examples
        return [task[:100] + "..." if len(task) > 100 else task for task in tasks[:3]]
    
    async def execute_real_world_collaboration(self, task: str, tools: Optional[List[Callable]] = None) -> Dict[str, Any]:
        """
        Execute a collaboration that can optionally integrate with external tools
        """
        # Start with AI collaboration
        ai_result = await self.execute_adaptive_collaboration(task)
        
        # If tools are provided and the task might benefit from them, use them
        if tools:
            tool_results = []
            for tool in tools:
                try:
                    # This is a simplified approach - in practice, you'd need to determine
                    # which tools are appropriate for the task
                    tool_result = await asyncio.get_event_loop().run_in_executor(None, tool)
                    tool_results.append(tool_result)
                except Exception as e:
                    print(f"[ERROR] Tool execution failed: {e}")
                    tool_results.append({"error": str(e)})
            
            # Combine AI and tool results
            ai_result["tool_integrations"] = tool_results
        
        return ai_result


# Example usage demonstrating integration with Moltbot concepts
async def demo_integration():
    """Demonstrate how the multi-AI system integrates with existing workflows"""
    print("[INIT] Initializing Integrated Multi-AI Collaboration System")
    print("=" * 60)
    
    collaborator = IntegratedMultiAICollaborator()
    
    # Demo 1: Complex analytical task
    print("\n[DEMO] Demo 1: Complex Business Analysis Task")
    task1 = ("Analyze the current state of our multi-model AI system, "
             "identify optimization opportunities, and suggest improvements. "
             "Consider both technical and business aspects.")
    
    result1 = await collaborator.execute_smart_collaboration(task1)
    print(f"[DONE] Collaboration completed. Task ID: {result1['task_id']}")
    print(f"   Collaborators used: {len(result1['contributions'])}")
    
    # Demo 2: Technical coding task
    print("\n[DEMO] Demo 2: Technical Implementation Task")
    task2 = ("Design and outline a Python class structure for managing "
             "dynamic model switching in a multi-AI system. Include error "
             "handling and performance monitoring.")
    
    result2 = await collaborator.execute_smart_collaboration(task2)
    print(f"[DONE] Collaboration completed. Task ID: {result2['task_id']}")
    print(f"   Analysis: {result2['task_analysis']['complexity']} complexity")
    
    # Demo 3: Creative writing task
    print("\n[DEMO] Demo 3: Creative Writing Task")
    task3 = ("Write a creative story about an AI system that learns to "
             "collaborate more effectively with other AIs. Focus on character "
             "development and thematic depth.")
    
    result3 = await collaborator.execute_smart_collaboration(task3)
    print(f"[DONE] Collaboration completed. Task ID: {result3['task_id']}")
    print(f"   Execution order: {' -> '.join(result3['execution_order'])}")
    
    # Show insights
    print("\n[INSIGHTS] Collaboration Insights")
    insights = collaborator.get_collaboration_insights()
    for key, value in insights.items():
        if key != 'recent_activity':  # Skip the detailed log for brevity
            print(f"   {key}: {value}")
    
    print(f"\n[READY] System ready for real-world collaboration tasks!")
    print("=" * 60)
    
    return collaborator


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demo_integration())