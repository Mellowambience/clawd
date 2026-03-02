"""
MIST Mycelium — inter-agent pub/sub over WebSocket.
Each MIST node registers its URL in MYCELIUM_NODES.
Messages route by topic; offline nodes are silently skipped (non-fatal).
"""
import os
from typing import List
import aiohttp

# Populate from environment or AGENTS.md discovery
MYCELIUM_NODES: List[str] = [
    url.strip()
    for url in os.environ.get("MYCELIUM_NODES", "").split(",")
    if url.strip()
]

_inbox: List[dict] = []


async def publish_to_mycelium(message: dict) -> None:
    """Broadcast a message to all registered sibling nodes."""
    async with aiohttp.ClientSession() as session:
        for node_url in MYCELIUM_NODES:
            try:
                await session.post(
                    f"{node_url}/mycelium/receive",
                    json=message,
                    timeout=aiohttp.ClientTimeout(total=2),
                )
            except Exception:
                pass  # node offline — non-fatal, mycelium is eventually consistent


async def drain_mycelium_inbox() -> List[dict]:
    """Return and clear the inbox buffer for this cycle."""
    global _inbox
    msgs, _inbox = list(_inbox), []
    return msgs


async def receive_from_mycelium(message: dict) -> None:
    """Called by POST /mycelium/receive on this node."""
    _inbox.append(message)
