import asyncio
import websockets
import json

async def sniff():
    uri = "ws://localhost:18789"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Sending handshake...")
            
            # Send handshake
            handshake = {
                "type": "req",
                "id": "diag-1",
                "method": "connect",
                "params": {"auth": {"token": "neural-console"}}
            }
            await websocket.send(json.dumps(handshake))
            
            # Send a test message
            chat_req = {
                "type": "req",
                "id": "diag-2",
                "method": "chat.send",
                "params": {"message": "hello diagnostic"}
            }
            await websocket.send(json.dumps(chat_req))
            print("Sent 'hello diagnostic'. Listening for 10 seconds...")

            # Listen loop
            for _ in range(20):
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(msg)
                    # Pretty print the payload structure
                    if data.get("type") == "event" and data.get("event") == "chat":
                         payload = data.get("payload", {})
                         print(f"\n[PACKET] RunID: {payload.get('runId')} | State: {payload.get('state')}")
                         content = payload.get("message", {}).get("content", [])
                         if content:
                             print(f"Content: {content[0].get('text')}")
                    else:
                        print(f"\n[OTHER] {msg}")
                except asyncio.TimeoutError:
                    break
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(sniff())
