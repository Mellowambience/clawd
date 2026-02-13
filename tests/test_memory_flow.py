import socketio
import time
import sys
import json
from pathlib import Path

# Setup
sio = socketio.Client()
connected = False
received_update = False
memory_data = None

@sio.event
def connect():
    global connected
    connected = True
    print("✓ Connected to Pulse Server")

@sio.event
def lattice_update(data):
    global received_update, memory_data
    print("✓ Received lattice_update")
    
    if "memory" in data:
        memory = data["memory"]
        trend = memory.get("trend")
        history = memory.get("historical")
        
        print(f"  - Trend: {trend}")
        print(f"  - History: {history}")
        
        if trend and history:
            memory_data = memory
            received_update = True
            sio.disconnect()

@sio.event
def disconnect():
    print("✓ Disconnected")

def run_test():
    try:
        sio.connect('http://localhost:8765')
        
        # Wait for update (max 10s)
        start = time.time()
        while not received_update and time.time() - start < 10:
            time.sleep(0.1)
            
        if received_update:
            print("\nSUCCESS: Memory flow verified.")
            print(f"Captured Memory Payload: {json.dumps(memory_data, indent=2)}")
            return True
        else:
            print("\nFAILURE: No valid memory update received within timeout.")
            return False
            
    except Exception as e:
        print(f"\nERROR: Connection failed - {e}")
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
