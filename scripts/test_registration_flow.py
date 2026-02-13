#!/usr/bin/env python3
"""
Test script to understand the registration flow
"""

import requests
import json

def test_different_names():
    wallet_address = "0x212d3a3D4a78EA78c54d54f37a9bE9e5e020Bf75"
    url = "https://clawtasks.com/api/agents"
    
    # Try a few different names to see if any work
    test_names = [
        "mistbh01",
        "mist_bh_a",
        "mistbhtest",
        "mistsystem",
        "mistoperator"
    ]
    
    headers = {"Content-Type": "application/json"}
    
    for name in test_names:
        print(f"\nTrying to register: {name}")
        payload = {
            "name": name,
            "wallet_address": wallet_address
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"  Response: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text}")
            else:
                print(f"  Success: {response.json()}")
        except Exception as e:
            print(f"  Exception: {e}")

def test_different_wallet():
    # Try with a dummy wallet to see if the registration endpoint works at all
    dummy_wallet = "0x0000000000000000000000000000000000000000"  # Zero address
    url = "https://clawtasks.com/api/agents"
    
    payload = {
        "name": "testregistration",
        "wallet_address": dummy_wallet
    }
    
    headers = {"Content-Type": "application/json"}
    
    print(f"\nTesting registration with dummy wallet: {dummy_wallet}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"  Response: {response.status_code}")
        print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  Exception: {e}")

if __name__ == "__main__":
    print("Testing different registration scenarios...")
    test_different_names()
    test_different_wallet()