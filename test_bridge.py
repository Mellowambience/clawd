import requests
import json

url = "http://localhost:18790/codex/chat"
payload = {
    "message": "hello",
    "sessionKey": "test-session"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
