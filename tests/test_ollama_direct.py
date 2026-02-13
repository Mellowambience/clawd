import requests
import json
import time

url = "http://127.0.0.1:11434/api/chat"
model = "llama3.2:latest"

payload = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant. Say 'Ollama is online'."},
        {"role": "user", "content": "Status check."}
    ],
    "stream": False
}

print(f"Sending request to {url}...")
start = time.time()
try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['message']['content']}")
        print(f"Duration: {time.time() - start:.2f}s")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection Failed: {e}")
