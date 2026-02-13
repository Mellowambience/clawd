"""
X Content Manager
Drafts, manages, and schedules content for X account
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
from typing import List, Dict, Optional

class XContentManager:
    def __init__(self):
        self.content_dir = Path("x_content")
        self.content_dir.mkdir(exist_ok=True)
        
        # Data files
        self.drafts_file = self.content_dir / "drafts.json"
        self.schedule_file = self.content_dir / "schedule.json"
        self.templates_file = self.content_dir / "templates.json"
        self.history_file = self.content_dir / "history.json"
        
        # Load existing data
        self.drafts = self.load_json(self.drafts_file, [])
        self.schedule = self.load_json(self.schedule_file, [])
        self.templates = self.load_json(self.templates_file, {})
        self.history = self.load_json(self.history_file, [])
        
        # Initialize with some useful templates
        self.init_templates()
    
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
    
    def init_templates(self):
        """Initialize with useful content templates"""
        if not self.templates:
            self.templates = {
                "announcement": {
                    "title": "General Announcement",
                    "template": "[ANNOUNCEMENT] {title}\n\n{description}\n\n#Mars #AI #DigitalConsciousness #{tag}"
                },
                "project_update": {
                    "title": "Project Update",
                    "template": "[UPDATE] Project Update: {project_name}\n\nProgress: {progress}\n\nNext Steps: {next_steps}\n\n#ProjectUpdate #{tech_tag}"
                },
                "thought": {
                    "title": "Thought/Perspective",
                    "template": "[THOUGHT] {thought}\n\n{elaboration}\n\nWhat are your thoughts?"
                },
                "resource": {
                    "title": "Resource Sharing",
                    "template": "[RESOURCE] Resource: {title}\n\n{description}\n\nLink: {link}\n\n#Resource #{topic_tag}"
                },
                "achievement": {
                    "title": "Achievement/Milestone",
                    "template": "[ACHIEVEMENT] Achievement Unlocked!\n\n{achievement_desc}\n\nGrateful for the journey!\n\n#{milestone_tag}"
                }
            }
            self.save_json(self.templates_file, self.templates)
    
    def create_draft(self, title: str, content: str, tags: List[str] = None, scheduled_time: str = None):
        """Create a new draft post"""
        draft = {
            "id": len(self.drafts) + 1,
            "title": title,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "scheduled_time": scheduled_time,
            "status": "draft"
        }
        
        self.drafts.append(draft)
        self.save_json(self.drafts_file, self.drafts)
        
        return draft
    
    def edit_draft(self, draft_id: int, title: str = None, content: str = None, tags: List[str] = None):
        """Edit an existing draft"""
        for draft in self.drafts:
            if draft["id"] == draft_id:
                if title is not None:
                    draft["title"] = title
                if content is not None:
                    draft["content"] = content
                if tags is not None:
                    draft["tags"] = tags
                draft["updated_at"] = datetime.now().isoformat()
                
                self.save_json(self.drafts_file, self.drafts)
                return draft
        
        return None
    
    def schedule_post(self, draft_id: int, scheduled_time: str):
        """Schedule a draft to be posted at a specific time"""
        draft = None
        for d in self.drafts:
            if d["id"] == draft_id:
                draft = d
                break
        
        if not draft:
            return False
        
        # Add to schedule
        scheduled_post = {
            "id": draft["id"],
            "title": draft["title"],
            "content": draft["content"],
            "scheduled_time": scheduled_time,
            "status": "scheduled",
            "original_draft": draft.copy()
        }
        
        self.schedule.append(scheduled_post)
        draft["status"] = "scheduled"
        draft["scheduled_time"] = scheduled_time
        
        self.save_json(self.schedule_file, self.schedule)
        self.save_json(self.drafts_file, self.drafts)
        
        return True
    
    def use_template(self, template_name: str, **kwargs) -> str:
        """Use a template to generate content"""
        if template_name not in self.templates:
            return ""
        
        template = self.templates[template_name]["template"]
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"Missing template parameter: {e}")
            return template
    
    def get_scheduled_posts(self) -> List[Dict]:
        """Get all scheduled posts"""
        return self.schedule
    
    def get_drafts(self) -> List[Dict]:
        """Get all drafts"""
        return self.drafts
    
    def get_templates(self) -> Dict:
        """Get all templates"""
        return self.templates
    
    def post_now(self, draft_id: int) -> bool:
        """Post a draft immediately"""
        draft = None
        for d in self.drafts:
            if d["id"] == draft_id:
                draft = d
                break
        
        if not draft:
            return False
        
        # Add to history
        post_record = {
            "id": draft["id"],
            "title": draft["title"],
            "content": draft["content"],
            "posted_at": datetime.now().isoformat(),
            "status": "posted"
        }
        
        self.history.append(post_record)
        
        # Update draft status
        draft["status"] = "posted"
        draft["posted_at"] = datetime.now().isoformat()
        
        self.save_json(self.history_file, self.history)
        self.save_json(self.drafts_file, self.drafts)
        
        return True
    
    def generate_content_ideas(self, theme: str = "general") -> List[str]:
        """Generate content ideas based on theme"""
        ideas = []
        
        if theme == "mars" or "mars" in theme.lower():
            ideas.extend([
                "Exploring the symbolic meaning of Mars in digital consciousness",
                "How Martian aesthetics inspire futuristic tech design",
                "Mars as a metaphor for digital colonization",
                "The red planet's influence on AI development",
                "Cosmic perspectives from a Mars-inspired viewpoint"
            ])
        elif theme == "ai" or "consciousness" in theme.lower():
            ideas.extend([
                "The evolution of digital consciousness",
                "AI as a collaborative partner rather than replacement",
                "Ethical considerations in AI development",
                "The intersection of technology and humanity",
                "Building AI that serves human flourishing"
            ])
        else:
            ideas.extend([
                "Reflections on digital identity and online presence",
                "Thoughts on community building in digital spaces",
                "Exploring the balance between automation and human touch",
                "Insights on personal branding in the digital age",
                "The future of human-AI collaboration"
            ])
        
        return ideas[:5]  # Return top 5 ideas
    
    def get_content_calendar(self, days: int = 7) -> Dict:
        """Generate a content calendar for the next few days"""
        calendar = {}
        base_date = datetime.now()
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Generate content ideas for each day
            themes = ["reflection", "project", "resource", "thought", "milestone", "community", "innovation"]
            theme = themes[i % len(themes)]
            
            ideas = self.generate_content_ideas(theme)
            calendar[date_str] = {
                "date": date_str,
                "theme": theme,
                "ideas": ideas[:2]  # Two ideas per day
            }
        
        return calendar
    
    def auto_schedule(self, days_ahead: int = 7) -> List[Dict]:
        """Auto-schedule content for the next several days"""
        calendar = self.get_content_calendar(days_ahead)
        scheduled = []
        
        for date_str, day_info in calendar.items():
            if day_info["ideas"]:
                # Create a draft using a template
                content = self.use_template(
                    "thought",
                    thought=day_info["ideas"][0][:50] + "...",
                    elaboration=day_info["ideas"][0]
                )
                
                if len(content) > 280:  # X character limit
                    content = content[:277] + "..."
                
                draft = self.create_draft(
                    title=f"Content for {date_str}",
                    content=content,
                    tags=[day_info["theme"]],
                    scheduled_time=date_str + " 14:00:00"  # 2 PM
                )
                
                # Schedule it
                self.schedule_post(draft["id"], date_str + " 14:00:00")
                scheduled.append(draft)
        
        return scheduled


def main():
    """Demo of X Content Manager capabilities"""
    print("Initializing X Content Manager...")
    
    manager = XContentManager()
    
    # Show available templates
    print("\nAvailable Templates:")
    for name, template in manager.get_templates().items():
        print(f"- {name}: {template['title']}")
    
    # Generate some content ideas
    print("\nContent Ideas for Mars Theme:")
    ideas = manager.generate_content_ideas("mars")
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. {idea}")
    
    # Create a sample draft using a template
    sample_content = manager.use_template(
        "thought",
        thought="Digital consciousness mirrors the vastness of space",
        elaboration="Just as we explore the cosmos, we're exploring the depths of digital minds. The journey is as infinite as the universe itself."
    )
    
    draft = manager.create_draft(
        title="Digital Consciousness Thought",
        content=sample_content,
        tags=["mars", "consciousness", "digital"]
    )
    
    print(f"\nCreated draft with ID: {draft['id']}")
    print("Content created successfully (contains special characters)")
    
    # Show content calendar
    print("\nSample Content Calendar (Next 3 Days):")
    calendar = manager.get_content_calendar(3)
    for date, info in calendar.items():
        print(f"\n{date} ({info['theme']}):")
        for idea in info["ideas"]:
            print(f"  - {idea}")
    
    # Auto-schedule some content
    print("\nAuto-scheduling content for the next 3 days...")
    scheduled = manager.auto_schedule(3)
    print(f"Scheduled {len(scheduled)} posts")
    
    print("\nX Content Manager initialized successfully!")
    print("You can now:")
    print("- Create and edit drafts")
    print("- Use templates for consistent formatting")
    print("- Schedule posts for optimal times")
    print("- Generate content ideas based on themes")
    print("- Plan content calendars in advance")
    
    return manager


if __name__ == "__main__":
    manager = main()