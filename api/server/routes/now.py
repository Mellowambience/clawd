"""
Routes: GET /api/v1/now
Returns: local time + active agent + latest weather summary
"""

import os
from datetime import datetime, timezone
import httpx
from fastapi import APIRouter

router = APIRouter()
DEFAULT_LAT = os.getenv("DEFAULT_LAT", "39.9526")
DEFAULT_LON = os.getenv("DEFAULT_LON", "-75.1652")


async def _fetch_weather_summary() -> dict:
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={DEFAULT_LAT}&longitude={DEFAULT_LON}"
            f"&current=temperature_2m,weathercode,windspeed_10m"
            f"&temperature_unit=fahrenheit&windspeed_unit=mph&timezone=America%2FNew_York"
        )
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(url)
            if r.status_code == 200:
                data = r.json().get("current", {})
                return {
                    "temp_f":      data.get("temperature_2m"),
                    "wind_mph":    data.get("windspeed_10m"),
                    "weathercode": data.get("weathercode"),
                    "source":      "open-meteo",
                }
    except Exception:
        pass
    return {"error": "weather unavailable"}


@router.get("/now")
async def now():
    dt      = datetime.now(timezone.utc).astimezone()
    weather = await _fetch_weather_summary()
    return {
        "datetime":     dt.isoformat(),
        "timezone":     os.getenv("TZ", "America/New_York"),
        "unix":         int(dt.timestamp()),
        "active_agent": os.getenv("MOTHERSHIP_HANDLE", "AMARA"),
        "weather":      weather,
        "afk_mode":     os.getenv("AFK_MODE", "false").lower() == "true",
        "sigil":        "✧⟁∅↺⇢≡~∴",
    }
