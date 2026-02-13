import requests
import json
import sys

print('Checking system status...')

# Check if UI server is running
try:
    response = requests.get('http://localhost:8083/api/stats', timeout=5)
    if response.status_code == 200:
        stats = response.json()
        print('UI Server: RUNNING')
        print(f'  Total Posts: {stats.get("total_posts", 0)}')
        print(f'  Avg Quality: {stats.get("avg_quality_score", 0)}')
        print(f'  Active Agents: {stats.get("active_agents", 0)}/{stats.get("total_agents", 0)}')
    else:
        print('UI Server: ISSUE - API not responding properly')
except Exception as e:
    print(f'UI Server: ERROR - {e}')

# Check actual backend
try:
    response = requests.get('http://localhost:8082/api/posts', timeout=5)
    if response.status_code == 200:
        posts = response.json()
        print(f'\nBackend: RUNNING')
        print(f'  Total Posts in System: {len(posts)}')
        if posts:
            print(f'  Sample Post: {posts[0].get("author", "Unknown")} - Quality: {posts[0].get("quality_score", 0)}')
    else:
        print('Backend: ISSUE - Not responding')
except Exception as e:
    print(f'Backend: ERROR - {e}')

# Check if X integration is working
try:
    # Check if there are any integration processes running
    import psutil
    x_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'hub_x' in ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else '':
                x_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if x_processes:
        print(f'\nX Integration: ACTIVE ({len(x_processes)} processes)')
    else:
        print('\nX Integration: INACTIVE')
except:
    print('\nX Integration: CHECK FAILED (psutil not available)')

# Check if agents are generating content appropriately
try:
    response = requests.get('http://localhost:8083/api/posts', timeout=5)
    if response.status_code == 200:
        posts = response.json()
        print(f'\nContent Generation: ACTIVE ({len(posts)} recent posts)')
        if posts:
            quality_scores = [p.get('quality_score', 0) for p in posts]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            print(f'  Average Quality of Recent Posts: {avg_quality:.2f}')
            threshold_met = "YES" if avg_quality >= 2.7 else "NO"
            print(f'  Quality Threshold Met: {threshold_met}')
    else:
        print('Content Generation: ISSUE - Cannot fetch recent posts')
except Exception as e:
    print(f'Content Generation: ERROR - {e}')

print(f'\nSystem verification complete.')