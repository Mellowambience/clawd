# gateway/mycelium.py
"""Mycelium - MIST inter-agent pub/sub layer."""
import os
from typing import List
import aiohttp

MYCELIUM_NODES: List[str] = [
    n.strip() for n in os.environ.get("MYCELIUM_PEERS", "").split(",") if n.strip()
]

_inbox: List[dict] = []


async def publish_to_mycelium(message: dict) -> None:
    async with aiohttp.ClientSession() as session:
        for node_url in MYCELIUM_NODES:
            try:
                await session.post(f"tnode_url}/mycelium/receive", json=message,
                                   timeout=aiohttp.ClientTimeout(total=2))
            except Exception:
                pass


async def drain_mycelium_inbox() -> List[dict]:
    global _inbox
    msgs, _inbox = list(_inbox), []
    return msgs


async def receive_from_mycelium(message: dict) -> None:
    _inbox.append(message)
