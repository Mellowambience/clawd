import requests
import json

try:
    # Test the backend API
    r = requests.get('http://localhost:8082/api/posts')
    print(f"Backend API status: {r.status_code}")
    
    if r.status_code == 200:
        posts = r.json()
        print(f"Found {len(posts)} posts")
        
        for i, post in enumerate(posts[:5]):  # Show first 5
            author = post.get("author", "Unknown")
            quality = post.get("quality_score", 0)
            content_preview = post.get("content", "")[:50] + "..."
            print(f"  {i+1}. {author}: Quality={quality}, Content='{content_preview}'")
    else:
        print("Could not connect to backend API")
        
except Exception as e:
    print(f"Error connecting to backend: {e}")

# Test the UI server
try:
    r2 = requests.get('http://localhost:8083/api/posts')
    print(f"\nUI Server API status: {r2.status_code}")
    
    if r2.status_code == 200:
        posts2 = r2.json()
        print(f"UI Server found {len(posts2)} posts")
        
        for i, post in enumerate(posts2[:3]):  # Show first 3
            author = post.get("author", "Unknown")
            quality = post.get("quality_score", 0)
            content_preview = post.get("content", "")[:50] + "..."
            print(f"  {i+1}. {author}: Quality={quality}, Content='{content_preview}'")
    else:
        print("Could not connect to UI server API")
        
except Exception as e:
    print(f"Error connecting to UI server: {e}")