"""
Routes: GET /api/v1/ecosystem/status
"""

import os, time
import redis.asyncio as aioredis
from fastapi import APIRouter

router = APIRouter()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def _redis_ok() -> bool:
    try:
        r = aioredis.from_url(REDIS_URL, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        return True
    except Exception:
        return False


@router.get("/ecosystem/status")
async def ecosystem_status():
    redis_healthy = await _redis_ok()
    return {
        "status": "online",
        "version": os.getenv("MOTHERSHIP_VERSION", "0.1.0"),
        "services": {
            "mist":    "healthy",
            "redis":   "healthy" if redis_healthy else "unavailable",
            "weather": "healthy",
            "sync":    "disabled",
        },
        "local_first": True,
        "afk_mode":    os.getenv("AFK_MODE", "false").lower() == "true",
        "uptime_ms":   int(time.time() * 1000),
        "sigil":       "✧⟁∅↺⇢≡~∴",
    }
