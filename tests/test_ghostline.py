
import asyncio
import websockets
import json
import uuid

async def test_ghostline_protocol():
    uri = "ws://localhost:18789"
    async with websockets.connect(uri) as websocket:
        print("[CONNECTED] Connected to MIST Gateway")

        # --- Test 1: Simple Chat ---
        req_id = str(uuid.uuid4())
        msg = {
            "method": "chat.send",
            "id": req_id,
            "params": {
                "message": "Hello MIST, verify status.",
                "sessionKey": "ghostline_test"
            }
        }
        await websocket.send(json.dumps(msg))
        print(f"[SENT] {msg['params']['message']}")

        response_chunks = []
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                
                if data.get("type") == "res":
                    print(f"[ACK] Run ID: {data['payload']['runId']}")
                
                elif data.get("type") == "event":
                    payload = data.get("payload", {})
                    event_type = data.get("event")
                    
                    if event_type == "thought":
                        print(f"[THOUGHT] {payload.get('text')}")
                    
                    elif event_type == "chat":
                        state = payload.get("state")
                        content = payload.get("message", {}).get("content", [{}])[0].get("text", "")
                        
                        if state == "tool_call":
                            print(f"[TOOL CALL DETECTED] {content}")
                            if "TOOL_OUTPUT" in content:
                                print("[FAIL] ALARM: Model hallucinated TOOL_OUTPUT!")
                                return
                            if content.strip().endswith("]]"):
                                print("[PASS] Stop sequence worked perfectly.")
                            else:
                                print(f"[WARN] Did not stop at ]]: '{content}'")
                        
                        elif state == "final":
                            print(f"[FINAL RESP] {content}")
                            response_chunks.append(content)
                            break
                    
                    elif event_type == "error":
                        print(f"[ERROR] {payload.get('error')}")
                        return

            except asyncio.TimeoutError:
                print("[TIMEOUT] No response in 10s")
                break

        # --- Test 2: Tool Use (Router) ---
        print("\n--- Test 2: Tool Request ---")
        req_id = str(uuid.uuid4())
        msg = {
            "method": "chat.send",
            "id": req_id,
            "params": {
                "message": "List current directory files.",
                "sessionKey": "ghostline_test"
            }
        }
        await websocket.send(json.dumps(msg))
        print(f"[SENT] {msg['params']['message']}")

        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=20.0)
                data = json.loads(message)
                
                if data.get("type") == "event":
                    payload = data.get("payload", {})
                    event_type = data.get("event")
                    
                    if event_type == "thought":
                        print(f"[THOUGHT] {payload.get('text')}")
                    
                    elif event_type == "chat":
                        state = payload.get("state")
                        content = payload.get("message", {}).get("content", [{}])[0].get("text", "")
                        
                        if state == "tool_call":
                            print(f"[TOOL EXEC] {content}")
                            # Ghostline Pass Condition: The tool call is emitted, then the loop continues internally on server
                            # We just watch for the FINAL response which must contain file info.
                        
                        elif state == "final":
                            print(f"[FINAL RESP] {content}")
                            if "list_dir" in content or "py" in content or "file" in content.lower():
                                print("[PASS] Tool output was integrated into final response.")
                            else:
                                print("[WARN] Response may not have used tool data.")
                            break

            except asyncio.TimeoutError:
                print("[TIMEOUT] No response in 20s (Tool likely hung or failed)")
                break

if __name__ == "__main__":
    asyncio.run(test_ghostline_protocol())
