import asyncio
import websockets
import json

async def test_mist_chat():
    uri = "ws://127.0.0.1:18789"
    
    async with websockets.connect(uri) as websocket:
        # Send handshake
        handshake = {
            "method": "handshake",
            "id": "test-1",
            "params": {}
        }
        await websocket.send(json.dumps(handshake))
        response = await websocket.recv()
        print("Handshake response:", response)
        
        # Send chat message
        chat_msg = {
            "method": "chat",
            "id": "test-2",
            "params": {
                "message": "hi",
                "session": "test-session"
            }
        }
        await websocket.send(json.dumps(chat_msg))
        print("Sent: hi")
        
        # Wait for response
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received: {data}")
            if data.get("type") == "stream.final":
                break

asyncio.run(test_mist_chat())
