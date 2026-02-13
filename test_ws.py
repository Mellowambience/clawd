import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://localhost:18789"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Send handshake
            handshake = {
                "type": "req",
                "id": "test-1",
                "method": "connect",
                "params": {"auth": {"token": "neural-console"}}
            }
            await websocket.send(json.dumps(handshake))
            print("Handshake sent.")
            
            response = await websocket.recv()
            print(f"Received: {response}")
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
