"""
Routes: GET /api/v1/radio/now-playing, POST /api/v1/radio/request
"""

import os, json
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel

router   = APIRouter()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_state: dict = {"current_track": None, "queue": [], "session_memory": []}


async def _redis():
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(REDIS_URL, socket_connect_timeout=2, decode_responses=True)
        await r.ping()
        return r
    except Exception:
        return None

async def _get():
    r = await _redis()
    if r:
        try:
            raw = await r.get("radio:state")
            if raw: return json.loads(raw)
        finally:
            await r.aclose()
    return _state

async def _set(s):
    global _state
    _state = s
    r = await _redis()
    if r:
        try: await r.set("radio:state", json.dumps(s))
        finally: await r.aclose()


class TrackRequest(BaseModel):
    query: str
    requested_by: str = "user"
    source: str = "text"


@router.get("/radio/now-playing")
async def radio_now_playing():
    s = await _get()
    return {
        "current_track":  s.get("current_track"),
        "queue_depth":    len(s.get("queue", [])),
        "next_track":     s["queue"][0] if s.get("queue") else None,
        "session_memory": s.get("session_memory", [])[-5:],
    }

@router.post("/radio/request")
async def radio_request(req: TrackRequest):
    s = await _get()
    track = {"query": req.query, "requested_by": req.requested_by, "source": req.source, "queued_at": datetime.now(timezone.utc).isoformat()}
    s.setdefault("queue", []).append(track)
    s.setdefault("session_memory", []).append(track)
    await _set(s)
    return {"queued": True, "track": track, "queue_depth": len(s["queue"])}
