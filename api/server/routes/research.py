"""
Routes: GET /api/v1/research/{topic}
v0 scaffold — LangGraph agent wiring in v1
"""

from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()

@router.get("/research/{topic}")
async def research(topic: str, depth: str = "standard"):
    return {
        "topic": topic, "depth": depth, "status": "queued",
        "version": "v0-scaffold",
        "message": f"Research pipeline for '{topic}' queued — LangGraph agent wiring in v1.",
        "sources": [], "synthesis": None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
