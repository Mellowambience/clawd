import asyncio
import websockets
import json
import time

async def test_gateway():
    uri = "ws://127.0.0.1:18789"
    async with websockets.connect(uri) as websocket:
        # 1. Connect
        print("Connecting...")
        connect_req = {
            "type": "req",
            "id": "connect-1",
            "method": "connect",
            "params": {
                "minProtocol": 3,
                "maxProtocol": 3,
                "auth": {"token": "secret123"},
                "client": {"id": "test-script", "version": "1.0", "platform": "cli", "mode": "test"}
            }
        }
        await websocket.send(json.dumps(connect_req))
        res = await websocket.recv()
        print(f"Connect Response: {res}")
        
        # 2. Send Chat
        print("Sending 'hello'...")
        chat_id = f"chat-{int(time.time())}"
        chat_req = {
            "type": "req",
            "id": chat_id,
            "method": "chat.send",
            "params": {
                "sessionKey": "test-session",
                "message": "hello",
                "idempotencyKey": f"idem-{int(time.time())}"
            }
        }
        await websocket.send(json.dumps(chat_req))
        
        # 3. Listen for response
        while True:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=20.0)
                data = json.loads(msg)
                if data.get("type") == "res" and data.get("id") == chat_id:
                     print(f"Ack: {msg}")
                elif data.get("type") == "event" and data.get("event") == "chat":
                    payload = data.get("payload", {})
                    state = payload.get("state")
                    content = payload.get("message", {}).get("content", [])
                    text = "".join([c["text"] for c in content if c["type"] == "text"])
                    print(f"Chat Event ({state}): {text}")
                    if state == "final":
                        break
            except asyncio.TimeoutError:
                print("Timeout waiting for response")
                break

asyncio.get_event_loop().run_until_complete(test_gateway())
