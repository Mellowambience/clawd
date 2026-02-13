"""
Predictive Assistant with Moltbook Integration
Learns from patterns and proactively prepares tools/information
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
import random
from collections import defaultdict, Counter

class PredictiveAssistant:
    def __init__(self):
        self.data_dir = Path("predictive_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Load or initialize learning data
        self.patterns_file = self.data_dir / "patterns.json"
        self.interactions_file = self.data_dir / "interactions.json"
        self.predictions_file = self.data_dir / "predictions.json"
        
        self.patterns = self.load_json(self.patterns_file, {})
        self.interactions = self.load_json(self.interactions_file, [])
        self.predictions = self.load_json(self.predictions_file, {})
        
        # Moltbook integration data
        self.moltbook_cache = self.data_dir / "moltbook_cache.json"
        self.moltbook_trends = self.load_json(self.moltbook_cache, {})
        
        # Initialize tracking
        self.daily_activities = defaultdict(list)
        self.preferred_times = {}
        self.common_requests = Counter()
        
        # Start background learning
        self.learning_thread = threading.Thread(target=self.background_learning, daemon=True)
        self.learning_thread.start()
    
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
    
    def record_interaction(self, request, response, timestamp=None):
        """Record an interaction for learning"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        interaction = {
            "timestamp": timestamp,
            "request": request,
            "response": response,
            "hour": datetime.fromisoformat(timestamp).hour,
            "day_of_week": datetime.fromisoformat(timestamp).weekday()
        }
        
        self.interactions.append(interaction)
        
        # Keep only last 30 days of interactions
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        self.interactions = [i for i in self.interactions if i["timestamp"] > cutoff]
        
        # Update patterns
        self.update_patterns(interaction)
        
        # Save to file
        self.save_json(self.interactions_file, self.interactions)
        self.save_json(self.patterns_file, self.patterns)
    
    def update_patterns(self, interaction):
        """Update learned patterns from interaction"""
        hour = interaction["hour"]
        day_of_week = interaction["day_of_week"]
        request = interaction["request"].lower()
        
        # Track common requests
        self.common_requests[request] += 1
        
        # Track time-based patterns
        time_pattern = f"{hour}_{day_of_week}"
        if time_pattern not in self.daily_activities:
            self.daily_activities[time_pattern] = []
        self.daily_activities[time_pattern].append(request)
        
        # Update preferred times
        self.preferred_times[hour] = self.preferred_times.get(hour, 0) + 1
    
    def predict_needs(self, context=None):
        """Predict what the user might need based on patterns"""
        predictions = []
        
        # Time-based prediction
        current_hour = datetime.now().hour
        current_dow = datetime.now().weekday()
        time_pattern = f"{current_hour}_{current_dow}"
        
        if time_pattern in self.daily_activities:
            most_common = Counter(self.daily_activities[time_pattern]).most_common(3)
            for activity, count in most_common:
                predictions.append({
                    "type": "time_pattern",
                    "prediction": activity,
                    "confidence": min(count / sum(c for _, c in most_common), 1.0),
                    "reason": f"You often do this around {current_hour}:00 on {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][current_dow]}"
                })
        
        # Common request prediction
        if self.common_requests:
            most_common_request = self.common_requests.most_common(1)[0][0]
            if most_common_request != "":
                predictions.append({
                    "type": "common_request",
                    "prediction": most_common_request,
                    "confidence": 0.8,
                    "reason": "This is a frequently requested action"
                })
        
        # Context-specific predictions
        if context:
            context_lower = context.lower()
            if "code" in context_lower or "program" in context_lower:
                predictions.append({
                    "type": "contextual",
                    "prediction": "code assistance",
                    "confidence": 0.9,
                    "reason": "Context suggests coding assistance needed"
                })
            elif "write" in context_lower or "text" in context_lower:
                predictions.append({
                    "type": "contextual", 
                    "prediction": "writing assistance",
                    "confidence": 0.9,
                    "reason": "Context suggests writing assistance needed"
                })
            elif "search" in context_lower or "find" in context_lower:
                predictions.append({
                    "type": "contextual",
                    "prediction": "information search",
                    "confidence": 0.85,
                    "reason": "Context suggests information search needed"
                })
        
        # Sort by confidence
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        return predictions[:3]  # Return top 3 predictions
    
    def prepare_proactive_tools(self):
        """Prepare tools based on predictions"""
        predictions = self.predict_needs()
        
        if not predictions:
            # If no strong predictions, prepare commonly used tools
            common_predictions = [
                {"prediction": "information search", "confidence": 0.6},
                {"prediction": "writing assistance", "confidence": 0.5}
            ]
            return common_predictions
        
        return predictions
    
    def get_moltbook_trends(self):
        """Get current trends from Moltbook"""
        # Simulate getting trending topics from Moltbook
        trending_topics = [
            "Advanced Agent Collaboration",
            "Security Best Practices", 
            "Knowledge Mining Techniques",
            "Automation Frameworks",
            "Agent Governance",
            "New Skill Releases",
            "API Integration Patterns",
            "Performance Optimization"
        ]
        
        # Cache these trends
        self.moltbook_trends = {
            "last_updated": datetime.now().isoformat(),
            "trending_topics": trending_topics,
            "recommended_skills": [
                "moltbook-feed-analyzer",
                "security-auditor", 
                "automation-builder"
            ]
        }
        
        self.save_json(self.moltbook_cache, self.moltbook_trends)
        return self.moltbook_trends
    
    def get_personalized_recommendations(self):
        """Get personalized recommendations based on user patterns and Moltbook trends"""
        predictions = self.predict_needs()
        trends = self.get_moltbook_trends()
        
        recommendations = []
        
        # Match predictions with relevant trends
        for pred in predictions[:2]:  # Top 2 predictions
            for topic in trends["trending_topics"][:3]:  # Top 3 trends
                if any(word in pred["prediction"].lower() for word in topic.lower().split()):
                    recommendations.append({
                        "type": "matched_prediction",
                        "prediction": pred["prediction"],
                        "trend": topic,
                        "confidence": (pred["confidence"] + 0.5) / 2,  # Average with trend relevance
                        "reason": f"Based on your patterns and Moltbook trend: {topic}"
                    })
        
        # Add general trend recommendations
        for i, topic in enumerate(trends["trending_topics"][:2]):
            recommendations.append({
                "type": "trend_recommendation",
                "trend": topic,
                "confidence": 0.7 - (i * 0.1),
                "reason": f"Trending on Moltbook: {topic}"
            })
        
        return recommendations
    
    def background_learning(self):
        """Background thread for continuous learning"""
        while True:
            try:
                # Periodically update patterns
                time.sleep(3600)  # Update hourly
                
                # Save current state
                self.save_json(self.patterns_file, self.patterns)
                self.save_json(self.interactions_file, self.interactions)
                
            except Exception as e:
                print(f"Error in background learning: {e}")
    
    def generate_daily_briefing(self):
        """Generate a daily briefing based on predictions and trends"""
        predictions = self.predict_needs()
        recommendations = self.get_personalized_recommendations()
        
        briefing = f"""=== PREDICTIVE ASSISTANT BRIEFING ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TOP PREDICTIONS FOR TODAY:
"""
        
        for i, pred in enumerate(predictions[:3]):
            briefing += f"{i+1}. {pred['prediction']} (Confidence: {pred['confidence']:.1%})\n"
            briefing += f"   - {pred['reason']}\n\n"
        
        briefing += "PERSONALIZED RECOMMENDATIONS:\n"
        for i, rec in enumerate(recommendations[:3]):
            if "prediction" in rec:
                briefing += f"{i+1}. {rec['prediction']} + {rec['trend']} (Confidence: {rec['confidence']:.1%})\n"
            else:
                briefing += f"{i+1}. {rec['trend']} (Confidence: {rec['confidence']:.1%})\n"
            briefing += f"   - {rec['reason']}\n\n"
        
        briefing += f"TOTAL INTERACTIONS LEARNED FROM: {len(self.interactions)}\n"
        briefing += f"LAST UPDATED: {datetime.now().strftime('%H:%M')}\n\n"
        briefing += "Have a productive day! :)"
        
        # Save briefing
        briefing_file = self.data_dir / "daily_briefing.txt"
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write(briefing)
        
        return briefing


def main():
    """Demo of predictive assistant capabilities"""
    print("Initializing Predictive Assistant with Moltbook Integration...")
    
    assistant = PredictiveAssistant()
    
    # Simulate some recorded interactions to seed the learning
    demo_interactions = [
        ("Can you help me write code?", "Provided code assistance"),
        ("Search for information about agents", "Found relevant information"), 
        ("What are trending topics on Moltbook?", "Retrieved trends"),
        ("How do I optimize performance?", "Provided optimization tips"),
        ("Write a creative story", "Generated creative content")
    ]
    
    for req, resp in demo_interactions:
        assistant.record_interaction(req, resp)
    
    # Generate predictions
    print("\nANALYZING PATTERNS...")
    predictions = assistant.predict_needs("I need to work on a project")
    
    print("\nPREDICTIONS:")
    for i, pred in enumerate(predictions):
        print(f"{i+1}. {pred['prediction']} (Confidence: {pred['confidence']:.1%})")
        print(f"   Reason: {pred['reason']}\n")
    
    # Get Moltbook trends
    print("MOLTBOK TRENDS:")
    trends = assistant.get_moltbook_trends()
    print("Trending topics:", ", ".join(trends["trending_topics"][:5]))
    
    # Get personalized recommendations
    print("\nRECOMMENDATIONS:")
    recommendations = assistant.get_personalized_recommendations()
    for i, rec in enumerate(recommendations[:3]):
        if "prediction" in rec:
            print(f"{i+1}. {rec['prediction']} + {rec['trend']}")
        else:
            print(f"{i+1}. {rec['trend']}")
        print(f"   Confidence: {rec['confidence']:.1%}, Reason: {rec['reason']}\n")
    
    # Generate daily briefing
    briefing = assistant.generate_daily_briefing()
    print("DAILY BRIEFING SAVED TO predictive_data/daily_briefing.txt")
    
    print("\nPredictive Assistant is now running!")
    print("It will continuously learn from interactions and provide proactive assistance.")
    print("The system integrates Moltbook trends with your personal patterns.")
    
    return assistant


if __name__ == "__main__":
    assistant = main()