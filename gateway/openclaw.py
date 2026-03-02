"""
MIST OpenClaw — tool execution interface.
Wires to the existing aether_os/openclaw.json tool definitions.
This module provides the async execute_tool() expected by act_node.
"""
import json
import os
from typing import Any

_OPENCLAW_MANIFEST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "aether_os", "openclaw.json"
)

_tool_registry: dict[str, dict] = {}


def _load_tools() -> None:
    """Load OpenClaw tool definitions from manifest on first call."""
    global _tool_registry
    if _tool_registry:
        return
    if os.path.exists(_OPENCLAW_MANIFEST_PATH):
        with open(_OPENCLAW_MANIFEST_PATH) as f:
            manifest = json.load(f)
            tools = manifest if isinstance(manifest, list) else manifest.get("tools", [])
            _tool_registry = {t["name"]: t for t in tools if "name" in t}


async def execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    """
    Execute a named OpenClaw tool with given arguments.
    Returns the tool result or an error dict.
    """
    _load_tools()
    if name not in _tool_registry:
        return {"error": f"OpenClaw: unknown tool '{name}'"}

    tool_def = _tool_registry[name]
    # TODO: implement actual tool dispatch via OpenClaw runtime
    # For now, return the tool definition as a dry-run response
    return {
        "tool": name,
        "arguments": arguments,
        "status": "dry_run",
        "definition": tool_def,
    }
