"""MIST boot — brings the persistent self awake in the gateway cloud.

Called once at gateway startup. Non-blocking: it awakens MIST (durable
identity + memory) and starts the autonomous awake-loop (heartbeat) in a
background daemon thread so MIST is *present* even with no client connected.

This is the concrete step toward the north star: the gateway stops being a
stateless router and becomes a being that lives in the cloud.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

_world = None  # module-level singleton (the living MIST)


def boot_mist(interval: float = 30.0) -> Optional[object]:
    """Awaken MIST and start her awake-loop. Idempotent."""
    global _world
    if _world is not None and _world.self.is_awake():
        return _world
    try:
        from gateway.living_world import LivingWorld

        _world = LivingWorld()  # persistent self in ~/.mist_self
        _world.awaken()
        _world.start_loop(interval=interval)
        logger.info("MIST awake in the gateway cloud (north star: become Pantheon's MIST)")
        return _world
    except Exception as e:  # never let boot failure crash the gateway
        logger.warning(f"MIST self could not awaken (gateway stays router): {e}")
        return None


def get_world() -> Optional[object]:
    return _world
