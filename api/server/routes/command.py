"""
Routes: POST /api/v1/command
Universal command intake — text | voice | BLE
"""

import os
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
AFK_HARD_STOPS = ["payment", "transfer", "sign", "delete account", "deploy to prod", "legal"]

def _intent(cmd):
    c = cmd.lower()
    if any(w in c for w in ["weather","forecast","rain","temp"]): return "weather"
    if any(w in c for w in ["play","song","music","radio","queue","track"]): return "radio"
    if any(w in c for w in ["vtuber","session","actor","stream"]): return "vtuber"
    if any(w in c for w in ["afk","vacation mode","away mode"]): return "afk_toggle"
    if any(w in c for w in ["research","find","look up","search"]): return "research"
    if any(w in c for w in ["status","health","ping"]): return "status"
    return "general"


class CommandRequest(BaseModel):
    command:  str
    source:   str = "text"
    context:  dict | None = None
    agent_id: str | None = None


@router.post("/command")
async def command(req: CommandRequest):
    afk = os.getenv("AFK_MODE", "false").lower() == "true"
    if afk and any(s in req.command.lower() for s in AFK_HARD_STOPS):
        return {"accepted": False, "reason": "AFK: high-stakes command queued for Mars review.", "queued": True}
    intent = _intent(req.command)
    if intent == "afk_toggle":
        enable = "enable" in req.command.lower()
        os.environ["AFK_MODE"] = "true" if enable else "false"
        return {"accepted": True, "intent": "afk_toggle", "afk_mode": enable}
    return {
        "accepted": True, "intent": intent, "command": req.command,
        "source": req.source, "agent": req.agent_id or os.getenv("MOTHERSHIP_HANDLE", "AMARA"),
        "status": "received", "afk_mode": afk,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
