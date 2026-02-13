"""
Interface for using the X Content Manager
"""

from x_content_manager import XContentManager
from datetime import datetime

def show_menu():
    """Display the main menu options"""
    print("\nOptions:")
    print("1. View drafts")
    print("2. Create new draft")
    print("3. View scheduled posts")
    print("4. View templates")
    print("5. Generate content ideas")
    print("6. View content calendar")
    print("7. Exit")

def handle_view_drafts(manager):
    """Handle viewing drafts option"""
    drafts = manager.get_drafts()
    if drafts:
        print(f"\nDrafts ({len(drafts)} total):")
        for draft in drafts:
            print(f"  ID: {draft['id']}")
            print(f"  Title: {draft['title']}")
            print(f"  Status: {draft['status']}")
            print(f"  Tags: {', '.join(draft['tags'])}")
            print(f"  Content Preview: {draft['content'][:100]}...")
            print()
    else:
        print("\nNo drafts found.")

def handle_create_draft(manager):
    """Handle creating a new draft option"""
    title = input("Enter title: ")
    print("Choose a template:")
    templates = manager.get_templates()
    for i, (name, template) in enumerate(templates.items(), 1):
        print(f"  {i}. {name}: {template['title']}")
    
    template_choice = input("Enter template number (or press Enter for custom): ").strip()
    
    if template_choice.isdigit() and 1 <= int(template_choice) <= len(templates):
        template_names = list(templates.keys())
        template_name = template_names[int(template_choice) - 1]
        
        print(f"\nUsing template: {template_name}")
        
        # Get template parameters
        params = {}
        if template_name == "thought":
            params["thought"] = input("Main thought: ")
            params["elaboration"] = input("Elaboration: ")
        elif template_name == "announcement":
            params["title"] = input("Title: ") or title
            params["description"] = input("Description: ")
            params["tag"] = input("Tag: ")
        elif template_name == "project_update":
            params["project_name"] = input("Project name: ")
            params["progress"] = input("Progress: ")
            params["next_steps"] = input("Next steps: ")
            params["tech_tag"] = input("Tech tag: ")
        elif template_name == "resource":
            params["title"] = input("Resource title: ")
            params["description"] = input("Description: ")
            params["link"] = input("Link: ")
            params["topic_tag"] = input("Topic tag: ")
        elif template_name == "achievement":
            params["achievement_desc"] = input("Achievement description: ")
            params["milestone_tag"] = input("Milestone tag: ")
        
        content = manager.use_template(template_name, **params)
        
        # Truncate if too long
        if len(content) > 280:
            content = content[:277] + "..."
        
    else:
        content = input("Enter content: ")
    
    tags_input = input("Enter tags (comma-separated): ")
    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
    
    draft = manager.create_draft(title, content, tags)
    print(f"Draft created with ID: {draft['id']}")

def handle_view_scheduled_posts(manager):
    """Handle viewing scheduled posts option"""
    scheduled = manager.get_scheduled_posts()
    if scheduled:
        print(f"\nScheduled Posts ({len(scheduled)} total):")
        for post in scheduled:
            print(f"  ID: {post['id']}")
            print(f"  Title: {post['title']}")
            print(f"  Scheduled: {post['scheduled_time']}")
            print()
    else:
        print("\nNo scheduled posts found.")

def handle_view_templates(manager):
    """Handle viewing templates option"""
    templates = manager.get_templates()
    print(f"\nTemplates ({len(templates)} total):")
    for name, template in templates.items():
        print(f"  {name}: {template['title']}")
        print(f"     Example: {template['template'][:100]}...")
        print()

def handle_generate_content_ideas(manager):
    """Handle generating content ideas option"""
    theme = input("Enter theme for content ideas (or press Enter for general): ").strip()
    if not theme:
        theme = "general"
    
    ideas = manager.generate_content_ideas(theme)
    print(f"\nContent Ideas for '{theme}' theme:")
    for i, idea in enumerate(ideas, 1):
        print(f"  {i}. {idea}")

def handle_view_content_calendar(manager):
    """Handle viewing content calendar option"""
    days = input("Enter number of days for calendar (default 7): ").strip()
    try:
        days = int(days) if days else 7
    except ValueError:
        days = 7
    
    calendar = manager.get_content_calendar(days)
    print(f"\nContent Calendar for Next {days} Days:")
    for date, info in list(calendar.items())[:7]:  # Show max 7 days
        print(f"\n{date} ({info['theme']}):")
        for idea in info["ideas"]:
            print(f"  - {idea}")

def main():
    manager = XContentManager()
    
    print("X Content Manager Interface")
    print("==========================")
    
    # Mapping of choices to handler functions
    handlers = {
        "1": handle_view_drafts,
        "2": handle_create_draft,
        "3": handle_view_scheduled_posts,
        "4": handle_view_templates,
        "5": handle_generate_content_ideas,
        "6": handle_view_content_calendar
    }
    
    while True:
        show_menu()
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice in handlers:
            handlers[choice](manager)
        elif choice == "7":
            print("Exiting X Content Manager...")
            break
        else:
            print("Invalid choice. Please enter 1-7.")

if __name__ == "__main__":
    main()