"""
Routes: GET /api/v1/weather/local, GET /api/v1/weather/personalized
Source: Open-Meteo (free, no key) + NWS fallback
Default location: Philadelphia, PA
"""

import os
import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter()
DEFAULT_LAT = os.getenv("DEFAULT_LAT", "39.9526")
DEFAULT_LON = os.getenv("DEFAULT_LON", "-75.1652")

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Showers", 82: "Heavy showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail",
}


async def _open_meteo(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,apparent_temperature,weathercode,windspeed_10m,precipitation"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
        f"&temperature_unit=fahrenheit&windspeed_unit=mph"
        f"&precipitation_unit=inch&timezone=America%2FNew_York&forecast_days=3"
    )
    async with httpx.AsyncClient(timeout=8) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()


async def _nws_fallback(lat, lon):
    try:
        async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "aetherhaven-mist/0.1"}) as client:
            pts = await client.get(f"https://api.weather.gov/points/{lat},{lon}")
            pts.raise_for_status()
            fc  = await client.get(pts.json()["properties"]["forecast"])
            fc.raise_for_status()
            return {"source": "nws", "periods": fc.json()["properties"]["periods"][:6]}
    except Exception:
        return None


@router.get("/weather/local")
async def weather_local(lat: str = DEFAULT_LAT, lon: str = DEFAULT_LON):
    try:
        data    = await _open_meteo(lat, lon)
        current = data.get("current", {})
        code    = current.get("weathercode", 0)
        return {
            "source": "open-meteo",
            "location": {"lat": lat, "lon": lon},
            "current": {
                "temp_f":       current.get("temperature_2m"),
                "feels_like_f": current.get("apparent_temperature"),
                "condition":    WMO_CODES.get(code, "Unknown"),
                "weathercode":  code,
                "wind_mph":     current.get("windspeed_10m"),
                "precip_in":    current.get("precipitation"),
            },
            "daily_forecast": [
                {
                    "date":      data["daily"]["time"][i],
                    "high_f":    data["daily"]["temperature_2m_max"][i],
                    "low_f":     data["daily"]["temperature_2m_min"][i],
                    "precip_in": data["daily"]["precipitation_sum"][i],
                    "condition": WMO_CODES.get(data["daily"]["weathercode"][i], "Unknown"),
                }
                for i in range(min(3, len(data["daily"].get("time", []))))
            ],
        }
    except Exception as e:
        nws = await _nws_fallback(lat, lon)
        if nws:
            return nws
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/weather/personalized")
async def weather_personalized(lat: str = DEFAULT_LAT, lon: str = DEFAULT_LON):
    base    = await weather_local(lat, lon)
    current = base.get("current", {})
    temp    = current.get("temp_f") or 0
    code    = current.get("weathercode", 0)
    notes   = []
    if temp < 35:
        notes.append("Sub-35°F — indoor deep work conditions optimal.")
    elif temp > 85:
        notes.append("Hot — hydration reminder active.")
    if code in (95, 96):
        notes.append("Thunderstorm — atmospheric pressure drop often correlates with creative surge.")
    if code in (71, 73, 75):
        notes.append("Snow — Night Sovereignty conditions. Everything is quieter.")
    if not notes:
        notes.append("Conditions nominal.")
    base["personalized"] = {"for": "Mars / Philadelphia", "notes": notes}
    return base
