from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

try:
    from skyfield.api import load, wgs84  # type: ignore

    SKYFIELD_AVAILABLE = True
except Exception:
    SKYFIELD_AVAILABLE = False


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "ephemeris"
BSP_FILE = DATA_DIR / "de421.bsp"
CONFIG_FILE = ROOT / "ephemeris_config.json"

CACHE_TTL_SEC = 60.0
_CACHE: Dict[str, Any] = {"at": 0.0, "value": None}


@dataclass
class EphemConfig:
    lat: float
    lon: float
    elevation_m: float
    orb_deg: float


DEFAULT_CONFIG = EphemConfig(
    lat=39.9526,  # Philadelphia fallback
    lon=-75.1652,
    elevation_m=12.0,
    orb_deg=3.0,
)


def _read_config() -> EphemConfig:
    cfg = DEFAULT_CONFIG
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            cfg = EphemConfig(
                lat=float(data.get("lat", cfg.lat)),
                lon=float(data.get("lon", cfg.lon)),
                elevation_m=float(data.get("elevation_m", cfg.elevation_m)),
                orb_deg=float(data.get("orb_deg", cfg.orb_deg)),
            )
        except Exception:
            cfg = DEFAULT_CONFIG

    # Environment overrides (highest priority)
    cfg = EphemConfig(
        lat=float(os.getenv("EPHEM_LAT", cfg.lat)),
        lon=float(os.getenv("EPHEM_LON", cfg.lon)),
        elevation_m=float(os.getenv("EPHEM_ALT", cfg.elevation_m)),
        orb_deg=float(os.getenv("EPHEM_ORB", cfg.orb_deg)),
    )
    return cfg


def _angle_diff(a: float, b: float) -> float:
    diff = abs(a - b) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


def _compute_aspects(longitudes: Dict[str, float], orb_deg: float) -> List[Dict[str, Any]]:
    aspects = []
    aspect_defs = {
        0: "conjunction",
        60: "sextile",
        90: "square",
        120: "trine",
        180: "opposition",
    }
    names = list(longitudes.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a_name = names[i]
            b_name = names[j]
            diff = _angle_diff(longitudes[a_name], longitudes[b_name])
            for angle, label in aspect_defs.items():
                delta = abs(diff - angle)
                if delta <= orb_deg:
                    aspects.append(
                        {
                            "a": a_name,
                            "b": b_name,
                            "aspect": label,
                            "angle": angle,
                            "delta": round(delta, 3),
                        }
                    )
    return aspects


def _load_ephemeris():
    if not SKYFIELD_AVAILABLE:
        return None, "missing_dependency_skyfield"
    if not BSP_FILE.exists():
        return None, "missing_ephemeris_file"
    try:
        eph = load(str(BSP_FILE))
        ts = load.timescale()
        return (eph, ts), None
    except Exception:
        return None, "ephemeris_load_failed"


def get_cosmic_state() -> Dict[str, Any]:
    now = time.time()
    cached = _CACHE.get("value")
    if cached and (now - _CACHE.get("at", 0.0) < CACHE_TTL_SEC):
        return {**cached, "cached": True}

    cfg = _read_config()
    ephem, err = _load_ephemeris()
    if err:
        payload = {
            "ok": False,
            "error": err,
            "details": {
                "skyfield_available": SKYFIELD_AVAILABLE,
                "bsp_file": str(BSP_FILE),
                "config_file": str(CONFIG_FILE),
            },
        }
        _CACHE["value"] = payload
        _CACHE["at"] = now
        return payload

    eph, ts = ephem
    t = ts.now()

    observer = eph["earth"] + wgs84.latlon(cfg.lat, cfg.lon, cfg.elevation_m)
    bodies = {
        "sun": eph["sun"],
        "moon": eph["moon"],
        "mercury": eph["mercury"],
        "venus": eph["venus"],
        "mars": eph["mars"],
        "jupiter": eph["jupiter barycenter"],
        "saturn": eph["saturn barycenter"],
        "uranus": eph["uranus barycenter"],
        "neptune": eph["neptune barycenter"],
        "pluto": eph["pluto barycenter"],
    }

    body_states: Dict[str, Dict[str, Any]] = {}
    longitudes: Dict[str, float] = {}

    for name, body in bodies.items():
        astrometric = observer.at(t).observe(body)
        ra, dec, distance = astrometric.radec()
        alt, az, _dist = astrometric.apparent().altaz()

        entry = {
            "ra_deg": round(ra.degrees, 6),
            "dec_deg": round(dec.degrees, 6),
            "alt_deg": round(alt.degrees, 6),
            "az_deg": round(az.degrees, 6),
            "distance_au": round(distance.au, 6),
        }

        try:
            ecl_lat, ecl_lon, _ecl_dist = astrometric.ecliptic_latlon()
            entry["ecl_lon_deg"] = round(ecl_lon.degrees, 6)
            longitudes[name] = ecl_lon.degrees
        except Exception:
            entry["ecl_lon_deg"] = None

        body_states[name] = entry

    aspects = _compute_aspects(longitudes, cfg.orb_deg) if longitudes else []

    payload = {
        "ok": True,
        "timestamp": now,
        "location": {
            "lat": cfg.lat,
            "lon": cfg.lon,
            "elevation_m": cfg.elevation_m,
        },
        "bodies": body_states,
        "aspects": aspects,
        "orb_deg": cfg.orb_deg,
    }

    _CACHE["value"] = payload
    _CACHE["at"] = now
    return payload
