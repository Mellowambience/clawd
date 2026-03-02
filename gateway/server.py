# gateway/server.py
"""MIST FastAPI Gateway - WebSocket + REST. Run: python gateway/server.py"""
import json
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
app = FastAPI(title="MIST Gateway", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "sovereign", "port": 18789, "version": "1.0.0"}


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(id(websocket))
    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            from gateway.langgraph_operator import handle_ws_message
            response = await handle_ws_message(payload.get("message", ""),
                                                 payload.get("session_id", session_id))
            await websocket.send_text(json.dumps({"response": response}))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))


@app.post("/chat")
async def chat_endpoint(body: dict):
    from gateway.langgraph_operator import handle_ws_message
    return {"response": await handle_ws_message(body.get("message", ""), body.get("session_id", "http"))}


@app.post("/mycelium/receive")
async def mycelium_receive(body: dict):
    from gateway.mycelium import receive_from_mycelium
    await receive_from_mycelium(body)
    return {"ok": True}


@app.get("/sanctuary/telemetry")
async def telemetry():
    return {"status": "pulse", "note": "MIST is alive"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=18789, log_level="info")
