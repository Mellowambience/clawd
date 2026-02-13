import os
import json
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("OpenClawEngine")

class OpenClawEngine:
    def __init__(self):
        self.config = self.load_config()
        self.shell_access = False
        self.tools_enabled = False
        self.whatsapp_enabled = False
        self.system_status = {
            "core": "active",
            "whatsapp": "disabled",
            "filesystem": "read-only"
        }
        self._parse_capabilities()

    def load_config(self) -> Dict[str, Any]:
        config_path = Path.home() / ".clawdbot" / "moltbot.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        return {}

    def _parse_capabilities(self):
        # 1. Check Tool Use
        tools = self.config.get("tools") or {}
        elevated = tools.get("elevated") or {}
        self.tools_enabled = elevated.get("enabled", False)
        
        if self.tools_enabled:
            # Grant shell access if tools are enabled (OpenClaw standard)
            self.shell_access = True
            self.system_status["filesystem"] = "write-access"
            logger.info("OpenClaw: Shell Access GRANTED")
        
        # 2. Check WhatsApp
        channels = self.config.get("channels") or {}
        wa_conf = channels.get("whatsapp") or {}
        if wa_conf.get("enabled", False) or wa_conf.get("allowFrom"):
            self.whatsapp_enabled = True
            self.system_status["whatsapp"] = "standby"

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Executes a local tool if permitted."""
        if not self.tools_enabled:
            return "❌ Tool use is disabled in OpenClaw config."
            
        logger.info(f"OpenClaw Executing: {tool_name} {args}")
        
        try:
            # Basic File Operations
            if tool_name == "read_file":
                path = args.get("path")
                if path and os.path.exists(path):
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        return f.read()[:20000]
                return "File not found."
                
            elif tool_name in ["list_dir", "listdir", "ls", "dir", "find"]:
                 path = args.get("path", ".")
                 return str(os.listdir(path))
                 
            elif tool_name in ["write_file", "create_file", "save"]:
                path = args.get("path") or args.get("filename")
                content = args.get("content")
                if path and content is not None:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    return f"Successfully wrote to {path}"
                return "Missing path/filename or content."

            elif tool_name == "tool_exists":
                check = args.get("key") or args.get("name")
                available = ["read_file", "list_dir", "write_file", "run_shell", "shadow_investigate"]
                return str(check in available).lower()

            # Shell Operations
            elif (tool_name == "run_shell" or tool_name == "cmd" or tool_name == "exec") and self.shell_access:
                cmd = args.get("command") or args.get("cmd")
                if not cmd: return "No command provided."
                
                # Basic Safety
                if any(x in cmd.lower() for x in ["del /s", "rm -rf", "format c:"]):
                    return "⚠️ Command blocked by Safety Protocol."

                try:
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=15)
                    output = stdout.decode(errors='ignore') + stderr.decode(errors='ignore')
                    return f"Exited with {process.returncode}:\n{output}"
                except asyncio.TimeoutError:
                    try: process.kill()
                    except: pass
                    return "⚠️ Command timed out after 15s."
                except Exception as e:
                    return f"Shell Error: {str(e)}"

            # Shadow Investigator Integration (RIN)
            elif tool_name == "shadow_investigate":
                query = args.get("query")
                if not query: return "Missing query parameter."
                
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.post("http://localhost:5006/api/chat", json={"query": query}) as r:
                            if r.status == 200:
                                data = await r.json()
                                return data.get("response", "No response from Shadow Pod.")
                            return f"Shadow Pod Uplink Error: {r.status}"
                except Exception as e:
                    return f"Shadow Pod Connection Failed: {e}"

            # OpenClaw / Aether.OS Standard Aliases
            elif tool_name == "scrutare": # Alias for list_dir/search
                return await self.execute_tool("list_dir", args)
                
            elif tool_name == "fabricare": # Alias for write/build
                return await self.execute_tool("write_file", args)
                
            elif tool_name == "reparare": # Alias for shell-based repair
                repair_cmd = args.get("command") or "python repair_soul.py"
                return await self.execute_tool("run_shell", {"command": repair_cmd})

            return f"Tool {tool_name} not available or permission denied."
            
        except Exception as e:
            return f"Execution Error: {str(e)}"

    def get_status_report(self) -> str:
        return f"""
OPENCLAW ENGINE STATUS:
-----------------------
Core: {self.system_status['core']}
WhatsApp: {self.system_status['whatsapp']} (Enabled: {self.whatsapp_enabled})
Filesystem: {self.system_status['filesystem']} (Write Access: {self.tools_enabled})
Shell Access: {'GRANTED' if self.shell_access else 'DENIED'}
Config Source: {Path.home() / ".clawdbot" / "moltbot.json"}
"""

# Singleton
engine = OpenClawEngine()
