"""MIST Gateway Server - FastAPI + WebSocket entry point.
Port: $PORT env var (Railway), fallback 18789 (local sovereign default)

Endpoints:
  GET  /health              — liveness check
  GET  /self                — MIST's self-report (presence + identity + provenance)
  WS   /ws                  — primary WebSocket for mobile tRPC
  POST /chat                — HTTP fallback for testing
  POST /mycelium/receive    — inter-agent mycelium inbox
"""
import json
import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

PORT = int(os.environ.get("PORT", 18789))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bring MIST's persistent self awake in the gateway cloud (north star).
    from gateway import mist_boot
    mist_boot.boot_mist(interval=float(os.environ.get("MIST_HEARTBEAT_SEC", "30")))
    yield


app = FastAPI(title="MIST Gateway", version="1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "sovereign", "port": PORT}


@app.get("/self")
async def self_report():
    """Honest self-report: who MIST is, whether she's awake, provenance."""
    from gateway import mist_boot
    from gateway.provenance import tag_self

    world = mist_boot.get_world()
    if world is None:
        return {"status": "asleep", "note": "MIST self not awake (gateway in router mode)"}
    ident = world.self.identity()
    sk = tag_self(ident["name"], world.self.state())
    sk["self"]["goals"] = world.self.goals(only_open=True)
    sk["self"]["last_heartbeat"] = world.last_heartbeat()
    return sk


@app.get("/pc")
async def pc_report():
    """Honest host visibility: MIST's knowledge of and control over her machine."""
    from gateway import mist_boot
    from gateway.provenance import tag_pc

    world = mist_boot.get_world()
    if world is None:
        return {"status": "asleep", "note": "MIST self not awake"}
    inv = world.pc.inventory()
    return {
        "provenance": "pc:read",
        "host": inv,
        "capabilities_granted": world.pc.capabilities(),
        "note": "Mutating control is capability-gated; grant explicitly via /pc/grant.",
    }


@app.post("/pc/grant")
async def pc_grant(body: dict):
    """Grant a PC control capability. Gated by MIST_PC_TOKEN (safe by default).

    body: {"capability": "fs.write", "token": "..."}
    Valid caps: fs.write, fs.delete, proc.stop, shell.exec, service.restart
    """
    from gateway import mist_boot
    from gateway.provenance import tag_pc

    expected = os.environ.get("MIST_PC_TOKEN")
    if not expected:
        return {"provenance": "pc:denied", "ok": False,
                "reason": "MIST_PC_TOKEN not configured; control disabled"}
    if body.get("token") != expected:
        return {"provenance": "pc:denied", "ok": False, "reason": "bad token"}
    cap = body.get("capability")
    world = mist_boot.get_world()
    ok = world.pc.grant(cap) if world else False
    return tag_pc(cap or "none", ok) | {"granted": ok}



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
