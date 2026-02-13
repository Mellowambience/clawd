"""
Test script to verify MIST Gateway connection and response.
"""
import asyncio
import json
import logging
import websockets
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_gateway():
    uri = "ws://localhost:18789"
    logging.info(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            logging.info("Connected!")
            
            # Send handshake
            msg_id = "test-1"
            handshake = {
                "type": "req",
                "id": msg_id,
                "method": "connect",
                "params": {"auth": {"token": "test-token"}}
            }
            await websocket.send(json.dumps(handshake))
            logging.info(f"Sent handshake: {handshake}")
            
            resp = await websocket.recv()
            logging.info(f"Received handshake response: {resp}")
            
            # Send chat message to test LLM
            chat_id = "test-2"
            chat_msg = {
                "type": "req",
                "id": chat_id,
                "method": "chat.send",
                "params": {
                    "sessionKey": "test-session",
                    "message": "Hello MIST, state your status."
                }
            }
            await websocket.send(json.dumps(chat_msg))
            logging.info(f"Sent chat message: {chat_msg['params']['message']}")
            
            # Wait for responses (ack + stream chunks + final)
            logging.info("Waiting for response stream...")
            start_time = datetime.now()
            
            while (datetime.now() - start_time).seconds < 30:
                try:
                    resp = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(resp)
                    
                    if data.get("type") == "event" and data.get("event") == "chat":
                        payload = data.get("payload", {})
                        state = payload.get("state")
                        content = payload.get("message", {}).get("content", [])
                        text = content[0].get("text", "") if content else ""
                        
                        if state == "stream":
                            print(f"{text}", end="", flush=True)
                        elif state == "final":
                            print(f"\n\n[FINAL RESPONSE]: {text}\n")
                            break
                        
                except asyncio.TimeoutError:
                    logging.warning("Timeout waiting for response chunk.")
                    break
                    
            logging.info("Test complete.")
            
    except Exception as e:
        logging.error(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_gateway())
