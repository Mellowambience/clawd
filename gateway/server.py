"""
MIST Gateway Server — FastAPI + WebSocket entry point.
Port: $PORT env var (Railway), fallback 18789 (local sovereign default)

Endpoints:
  GET  /health              — liveness check
  WS   /ws                  — primary WebSocket for mobile tRPC
  POST /chat                — HTTP fallback for testing
  POST /mycelium/receive    — inter-agent mycelium inbox
"""
import json
import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="MIST Gateway", version="1.0")

PORT = int(os.environ.get("PORT", 18789))


@app.get("/health")
async def health():
    return {"status": "sovereign", "port": PORT}


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(id(websocket))
    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            user_input = payload.get("message", "")
            sid = payload.get("session_id", session_id)

            # Import here to avoid circular imports at module load
            from scripts.mist_unified_operator import handle_ws_message
            response = await handle_ws_message(user_input, sid)

            await websocket.send_text(json.dumps({"response": response}))
    except WebSocketDisconnect:
        pass


@app.post("/chat")
async def chat_endpoint(body: dict):
    from scripts.mist_unified_operator import handle_ws_message
    response = await handle_ws_message(
        body["message"],
        body.get("session_id", "http"),
    )
    return {"response": response}


@app.post("/mycelium/receive")
async def mycelium_receive(body: dict):
    from gateway.mycelium import receive_from_mycelium
    await receive_from_mycelium(body)
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
