"""
Routes: GET /api/v1/vtuber/actors, POST /api/v1/vtuber/session/start
"""

import os, uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_db

router     = APIRouter()
ETH_WALLET = os.getenv("ETH_WALLET", "0x212d3a3D4a78EA78c54d54f37a9bE9e5e020Bf75")

ACTORS = [
    {"id": "actor-amara-v1", "handle": "AMARA∴", "type": "procedural", "model": "gemini-2.0-flash", "session_rate": {"amount": 25.0, "currency": "USD", "per": "2hr"}, "active": True},
    {"id": "actor-rin-v1",   "handle": "RIN$",   "type": "procedural", "model": "gemini-2.0-flash", "session_rate": {"amount": 20.0, "currency": "USD", "per": "2hr"}, "active": True},
]


class SessionStartRequest(BaseModel):
    actor_id: str
    session_type: str = "procedural"
    duration_hours: float = 2.0
    payment_trigger: dict | None = None
    user_handle: str | None = None


@router.get("/vtuber/actors")
async def vtuber_actors():
    return {"actors": ACTORS, "total": len(ACTORS), "eth_wallet": ETH_WALLET}


@router.post("/vtuber/session/start")
async def vtuber_session_start(req: SessionStartRequest):
    actor = next((a for a in ACTORS if a["id"] == req.actor_id), None)
    if not actor:
        raise HTTPException(status_code=404, detail=f"Actor '{req.actor_id}' not found")
    session_id = str(uuid.uuid4())
    now        = datetime.now(timezone.utc).isoformat()
    trigger    = req.payment_trigger or {"threshold_usd": actor["session_rate"]["amount"], "token": "ETH", "wallet": ETH_WALLET}
    async for db in get_db():
        await db.execute(
            "INSERT INTO vtuber_sessions (id,actor_id,session_type,duration_hours,payment_trigger,status,started_at) VALUES (?,?,?,?,?,?,?)",
            (session_id, req.actor_id, req.session_type, req.duration_hours, str(trigger), "active", now)
        )
        await db.commit()
    return {"session": {"id": session_id, "actor": actor["handle"], "status": "active", "started_at": now, "duration_hours": req.duration_hours, "payment_trigger": trigger}, "pay_to": ETH_WALLET}
