# gateway/openclaw.py
"""OpenClaw tool execution shim - routes to real openclaw engine or safe stub."""
import json
import os
import subprocess
from typing import Any


async def execute_tool(name: str, arguments: dict) -> Any:
    openclaw_config = os.path.join(os.path.dirname(__file__), "..", "aether_os", "openclaw.json")
    try:
        with open(openclaw_config) as f:
            config = json.load(f)
        tools = {t["name"]: t for t in config.get("tools", [])}
        if name not in tools:
            return {"status": "unknown_tool", "tool": name}
        tool_def = tools[name]
        if tool_def.get("type") == "shell":
            cmd = tool_def["command"].format(**arguments)
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {"status": "ok", "stdout": result.stdout, "stderr": result.stderr}
        return {"status": "dispatched", "tool": name, "arguments": arguments}
    except FileNotFoundError:
        return {"status": "stub", "tool": name, "note": "openclaw.json not found"}
    except Exception as e:
        return {"status": "error", "tool": name, "error": str(e)}
