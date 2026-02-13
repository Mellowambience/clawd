import requests
import json

url = "http://127.0.0.1:11434/v1/chat/completions"
# The model ID "mistral-32k" must match what's in 'ollama list'
payload = {
    "model": "mistral-32k",
    "messages": [{"role": "user", "content": "hi"}],
    "stream": False
}
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer ollama-local"
}

try:
    print(f"Testing {url} with auth header...")
    res = requests.post(url, json=payload, headers=headers)
    print(f"Status: {res.status_code}")
    print(res.text[:500])
except Exception as e:
    print(e)
