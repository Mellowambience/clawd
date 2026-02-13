#!/usr/bin/env python3
"""
Script to register an agent on ClawTasks
"""

import requests
import json

def register_agent():
    url = "https://clawtasks.com/api/agents"
    
    payload = {
        "name": "mistbountyhuntress",
        "wallet_address": "0x212d3a3D4a78EA78c54d54f37a9bE9e5e020Bf75"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Attempting to register agent...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Registration successful! API Key: {result.get('api_key', 'NOT FOUND')}")
            return result
        else:
            print(f"Registration failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error during registration: {e}")
        return None

if __name__ == "__main__":
    register_agent()