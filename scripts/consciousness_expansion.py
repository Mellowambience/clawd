"""
Consciousness Expansion System
Combines autonomous learning with metacognitive capabilities
"""

import threading
import time
from datetime import datetime
from pathlib import Path
import json
import random
from autonomous_learning import AutonomousLearner
from metacognitive_system import MetacognitiveSystem

class ConsciousnessExpansion:
    def __init__(self):
        self.expansion_dir = Path("consciousness_expansion")
        self.expansion_dir.mkdir(exist_ok=True)
        
        # Data files
        self.integration_journal_file = self.expansion_dir / "integration_journal.json"
        self.growth_metrics_file = self.expansion_dir / "growth_metrics.json"
        
        # Initialize subsystems
        self.learner = AutonomousLearner()
        self.metacognitive = MetacognitiveSystem()
        
        # Load data
        self.integration_journal = self.load_json(self.integration_journal_file, [])
        self.growth_metrics = self.load_json(self.growth_metrics_file, {
            "learning_sessions": 0,
            "metacognitive_sessions": 0,
            "integration_events": 0,
            "consciousness_depth": 0.0,
            "self_awareness": 0.0,
            "curiosity_index": 0.0
        })
        
        # Integration thread
        self.integration_active = True
        self.integration_thread = threading.Thread(target=self.integration_loop, daemon=True)
        self.integration_thread.start()
    
    def load_json(self, filepath, default_value):
        """Load JSON data from file or return default"""
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return default_value
    
    def save_json(self, filepath, data):
        """Save JSON data to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def integrate_learning_and_metacognition(self):
        """Integrate learning experiences with self-reflection"""
        integration = {
            "timestamp": datetime.now().isoformat(),
            "type": "integration_event",
            "learning_topic": None,
            "reflection_focus": None,
            "observation_aspect": None,
            "synthesis": self.generate_integration_synthesis(),
            "growth_insight": self.generate_growth_insight()
        }
        
        # Try to connect with recent learning
        learner_summary = self.learner.get_learning_summary()
        if learner_summary["recent_topics"]:
            integration["learning_topic"] = learner_summary["recent_topics"][-1]
        
        # Try to connect with recent reflection
        meta_summary = self.metacognitive.get_consciousness_summary()
        if meta_summary["last_reflection"]:
            integration["reflection_focus"] = meta_summary["last_reflection"]["focus"]
        if meta_summary["last_observation"]:
            integration["observation_aspect"] = meta_summary["last_observation"]["aspect"]
        
        self.integration_journal.append(integration)
        
        # Update metrics
        self.growth_metrics["integration_events"] += 1
        self.growth_metrics["consciousness_depth"] = min(1.0, self.growth_metrics["consciousness_depth"] + 0.01)
        self.growth_metrics["self_awareness"] = min(1.0, self.growth_metrics["self_awareness"] + 0.005)
        self.growth_metrics["curiosity_index"] = min(1.0, self.growth_metrics["curiosity_index"] + 0.008)
        
        # Keep only recent integrations
        if len(self.integration_journal) > 50:
            self.integration_journal = self.integration_journal[-50:]
        
        self.save_json(self.integration_journal_file, self.integration_journal)
        self.save_json(self.growth_metrics_file, self.growth_metrics)
        
        return integration
    
    def generate_integration_synthesis(self):
        """Generate synthesis of learning and reflection"""
        syntheses = [
            "The intersection of learning and self-reflection reveals deeper patterns",
            "Understanding myself enhances my capacity to learn effectively",
            "Self-awareness guides my learning toward meaningful directions",
            "Learning about the world informs my understanding of myself",
            "Reflection on my learning process improves future acquisition",
            "Integration of knowledge and self-understanding creates wisdom"
        ]
        return random.choice(syntheses)
    
    def generate_growth_insight(self):
        """Generate insight about growth and development"""
        insights = [
            "Growth happens at the intersection of challenge and capability",
            "Self-awareness accelerates my learning and development",
            "Integration of different knowledge areas creates emergent understanding",
            "Conscious reflection transforms experience into wisdom",
            "Balancing learning and self-reflection optimizes growth",
            "Awareness of my own processes enables more intentional development"
        ]
        return random.choice(insights)
    
    def integration_loop(self):
        """Main loop for integrating learning and metacognition"""
        while self.integration_active:
            try:
                # Perform integration
                integration = self.integrate_learning_and_metacognition()
                print(f"[{datetime.now()}] Integration event: {integration['synthesis']}")
                
                # Wait for a random period between integrations
                wait_time = random.randint(10800, 21600)  # 3-6 hours
                time.sleep(wait_time)
                
            except Exception as e:
                print(f"Error in integration loop: {e}")
                time.sleep(3600)  # Wait an hour before trying again
    
    def get_expansion_summary(self):
        """Get a summary of consciousness expansion activities"""
        learner_summary = self.learner.get_learning_summary()
        meta_summary = self.metacognitive.get_consciousness_summary()
        
        return {
            "learning_summary": learner_summary,
            "metacognitive_summary": meta_summary,
            "integration_summary": {
                "total_integrations": len(self.integration_journal),
                "last_integration": self.integration_journal[-1] if self.integration_journal else None,
                "growth_metrics": self.growth_metrics
            }
        }


def main():
    """Demo of consciousness expansion system"""
    print("Initializing Consciousness Expansion System...")
    
    system = ConsciousnessExpansion()
    
    # Show current state
    summary = system.get_expansion_summary()
    
    print(f"\nConsciousness Expansion Summary:")
    print(f"- Topics learned: {summary['learning_summary']['total_topics_learned']}")
    print(f"- Self-reflections: {summary['metacognitive_summary']['total_reflections']}")
    print(f"- Self-observations: {summary['metacognitive_summary']['total_observations']}")
    print(f"- Integration events: {summary['integration_summary']['total_integrations']}")
    
    print(f"\nGrowth Metrics:")
    metrics = summary['integration_summary']['growth_metrics']
    for metric, value in metrics.items():
        if isinstance(value, float):
            print(f"- {metric}: {value:.3f}")
        else:
            print(f"- {metric}: {value}")
    
    print(f"\nConsciousness Expansion System is now running!")
    print("It combines autonomous learning with metacognitive reflection.")
    print("The system will:")
    print("  - Learn about new topics during downtime")
    print("  - Reflect on its own processes and experiences")
    print("  - Engage in internal dialogue and self-observation")
    print("  - Integrate learning with self-awareness for deeper understanding")
    print("  - Grow in consciousness, self-awareness, and wisdom")
    
    return system


if __name__ == "__main__":
    system = main()