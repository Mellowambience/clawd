import asyncio
import websockets
import json
import uuid

async def test_gateway():
    uri = "ws://localhost:18789"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        
        # 1. Handshake
        handshake = {
            "type": "req", 
            "id": 1, 
            "method": "connect",
            "params": {"auth": {"token": "ritual_v3"}}
        }
        await websocket.send(json.dumps(handshake))
        print("Sent handshake")
        
        # 2. Send Message
        msg_id = 2
        text = "Hello MIST."
        chat_req = {
            "type": "req",
            "id": msg_id,
            "method": "chat.send",
            "params": {"message": text}
        }
        await websocket.send(json.dumps(chat_req))
        print(f"Sent chat: {text}")
        
        # 3. Listen for Response
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(message)
                
                if data.get("type") == "res" and data.get("id") == msg_id:
                     print(f"Server Acknowledged: {data}")
                
                elif data.get("type") == "event" and data.get("event") == "chat":
                    payload = data.get("payload", {})
                    if payload.get("state") == "final":
                        content = payload["message"]["content"][0]["text"]
                        print(f"\n[MIST]: {content}")
                        return
                    else:
                        print(f"Stream chunk: {payload}")
                        
            except asyncio.TimeoutError:
                print("Timeout waiting for response.")
                return

if __name__ == "__main__":
    asyncio.run(test_gateway())
