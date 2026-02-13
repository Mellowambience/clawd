# 🔧 Clawd Ecosystem: Issues & Solutions Tracker

**Generated:** 2026-02-08
**Status:** Active Development

---

## 📋 Issue Summary

| # | Issue | Severity | Status | Effort |
|---|-------|----------|--------|--------|
| 1 | UnicodeEncodeError in Logging | 🟡 Medium | Open | 5 min |
| 2 | WebSocket Connection Instability | 🟡 Medium | Open | 30 min |
| 3 | Disabled Silence/Void Features | 🟢 Low | Open | 15 min |
| 4 | Hardcoded Absolute Paths | 🟢 Low | Open | 1 hour |
| 5 | Missing OpenClaw Config | 🟡 Medium | Open | 10 min |
| 6 | No Graceful Shutdown Handler | 🟢 Low | Open | 20 min |
| 7 | Memory Truncation Too Aggressive | 🟢 Low | Open | 10 min |

---

## 🔴 Issue #1: UnicodeEncodeError in Logging

### Description
The gateway logs show frequent `UnicodeEncodeError` exceptions when trying to log messages containing special Unicode characters (glyphs like `↺`, `⟁`, `∅`).

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u21ba' 
in position 57: character maps to <undefined>
```

### Root Cause
Windows console uses `cp1252` encoding by default, which doesn't support extended Unicode characters used by the MIST persona system.

### Solution
**File:** `c:\Users\nator\clawd\moltbot\gateway\server.py`

**Option A: Configure logging with UTF-8 file handler (Recommended)**

Add this after line 36:
```python
# Configure UTF-8 file handler for logs
log_file = Path(__file__).resolve().parents[2] / "gateway.log"
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Fix console encoding for Windows
import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

**Option B: Sanitize glyph characters before logging**

Create a helper function:
```python
def safe_log(text: str) -> str:
    """Replace problematic Unicode characters for Windows logging."""
    replacements = {
        '↺': '[rotate]',
        '⟁': '[glyph]',
        '∅': '[null]',
        '⇢': '[arrow]',
        '≡': '[equiv]',
        '∴': '[therefore]',
    }
    result = text
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    return result
```

---

## 🟡 Issue #2: WebSocket Connection Instability

### Description
Frequent `websockets.exceptions.ConnectionClosedOK` errors and client disconnections/reconnections in the gateway log.

### Root Cause
- Missing ping/pong heartbeat mechanism
- No reconnection logic on client side
- Potential timeout issues

### Solution
**File:** `c:\Users\nator\clawd\moltbot\gateway\server.py`

**Add WebSocket configuration with ping/pong:**

Replace line 962:
```python
# OLD:
async with websockets.serve(self.handler, "0.0.0.0", PORT):

# NEW:
async with websockets.serve(
    self.handler, 
    "0.0.0.0", 
    PORT,
    ping_interval=30,      # Send ping every 30 seconds
    ping_timeout=10,       # Wait 10 seconds for pong
    close_timeout=5,       # Grace period for close handshake
    max_size=2**20,        # 1MB max message size
    compression=None       # Disable compression for stability
):
```

**Add connection error handling in handler:**

Update the `handler` method (line 881):
```python
async def handler(self, websocket):
    remote = websocket.remote_address
    await self.register(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                msg_id = data.get("id")
                method = data.get("method")
                params = data.get("params", {})

                if msg_type == "req":
                    if method == "connect":
                        await self.handle_connect(websocket, msg_id, params)
                    elif method == "chat.send":
                        asyncio.create_task(self.handle_chat(websocket, msg_id, params))
                    elif method == "ping":
                        # Add explicit ping handler
                        await websocket.send(json.dumps({"type": "pong", "id": msg_id}))
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON from {remote}: {e}")
            except Exception as e:
                logger.error(f"Error handling message: {e}")
    except websockets.exceptions.ConnectionClosedError as e:
        logger.info(f"Client {remote} disconnected unexpectedly: {e.code}")
    except websockets.exceptions.ConnectionClosedOK:
        logger.debug(f"Client {remote} disconnected gracefully")
    finally:
        await self.unregister(websocket)
```

---

## 🟢 Issue #3: Disabled Silence/Void Features

### Description
Lines 650-676 in `server.py` contain disabled silence mode and void input detection features with comments like "DISABLED: Silence checks reference undefined methods".

### Root Cause
The `send_stream_final` method exists (line 848), but the code was commented out. This appears to be a false assumption - the method is actually defined.

### Solution
**File:** `c:\Users\nator\clawd\moltbot\gateway\server.py`

**Re-enable the silence checks (lines 650-676):**

```python
# SILENCE MODE: Honor the silence flag
if self._silence_enabled() and not allow_diagnostic(user_message):
    await self.send_stream_final(websocket, run_id, "⟁")
    history = self._get_history(session_key)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": "(silence)"})
    self.save_history()
    return

# SILENCE REQUEST: User explicitly requests silence
if self._is_silence_request(user_message):
    await self.send_stream_final(websocket, run_id, "")
    history = self._get_history(session_key)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": "(silence)"})
    self.save_history()
    return

# VOID INPUT: Block suspicious input patterns
if self._should_void_input(user_message):
    await self.send_stream_final(websocket, run_id, "\u2205")
    history = self._get_history(session_key)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": "(voided)"})
    self.save_history()
    return
```

---

## 🟢 Issue #4: Hardcoded Absolute Paths

### Description
Many paths are hardcoded like `c:\\Users\\nator\\clawd\\...` throughout the codebase, making it non-portable.

### Root Cause
Development convenience; paths were set during initial development.

### Solution
**Create a centralized paths module:**

**New File:** `c:\Users\nator\clawd\moltbot\gateway\paths.py`

```python
"""Centralized path configuration for the Clawd ecosystem."""
from pathlib import Path

# Project root - 3 levels up from this file
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Core directories
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_DIR = PROJECT_ROOT / "memory"
MYCELIUM_DIR = PROJECT_ROOT / "mycelium"
LOGS_DIR = PROJECT_ROOT / "logs"

# Key files
HEARTBEAT_LOG = PROJECT_ROOT / "HEARTBEAT.log"
GATEWAY_LOG = PROJECT_ROOT / "gateway.log"
MEMORY_FILE = PROJECT_ROOT / "MEMORY.md"
ENV_FILE = PROJECT_ROOT / ".env"

# Data files
CHAT_HISTORY_FILE = DATA_DIR / "mist_chat_history.json"
GBL_SEED_FILE = DATA_DIR / "current_gbl_seed.txt"
SILENCE_FLAG = DATA_DIR / "silence.flag"
MAINTENANCE_FLAG = DATA_DIR / "maintenance_mode.flag"

# Personal IDE files
PERSONAL_IDE_DIR = PROJECT_ROOT / "personal-ide"
GRIMOIRE_FILE = PERSONAL_IDE_DIR / "GRIMOIRE.json"
SOUL_FILE = PERSONAL_IDE_DIR / "SOUL.md"

# MIST Identity
MIST_IDENTITY_FILE = PROJECT_ROOT / "mist_luna" / "MIST_IDENTITY.md"

# Hub files
HUB_DIR = PROJECT_ROOT / "clawdbot-hub"
HUB_DB_FILE = HUB_DIR / "data" / "db.json"

# Ensure directories exist
for dir_path in [DATA_DIR, MEMORY_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
```

**Then update imports in server.py:**
```python
from moltbot.gateway.paths import (
    PROJECT_ROOT, DATA_DIR, HEARTBEAT_LOG, CHAT_HISTORY_FILE,
    GBL_SEED_FILE, GRIMOIRE_FILE, SOUL_FILE, MIST_IDENTITY_FILE,
    MEMORY_DIR, HUB_DB_FILE, SILENCE_FLAG, MAINTENANCE_FLAG
)
```

---

## 🟡 Issue #5: Missing OpenClaw Config

### Description
The OpenClaw Engine looks for config at `~/.clawdbot/moltbot.json` which may not exist.

### Root Cause
No default configuration is created during setup.

### Solution
**Create default config if missing:**

**Update:** `c:\Users\nator\clawd\moltbot\gateway\openclaw_engine.py`

Add to `load_config` method:
```python
def load_config(self) -> Dict[str, Any]:
    config_path = Path.home() / ".clawdbot" / "moltbot.json"
    
    # Create default config if missing
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            "tools": {
                "elevated": {
                    "enabled": True,
                    "allowList": ["read_file", "write_file", "list_dir", "cmd"]
                }
            },
            "channels": {
                "whatsapp": {"enabled": False}
            },
            "safety": {
                "blockedCommands": ["del /s", "rm -rf", "format"]
            }
        }
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default OpenClaw config at {config_path}")
            return default_config
        except Exception as e:
            logger.error(f"Failed to create default config: {e}")
            return {}
    
    # Load existing config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}
```

---

## 🟢 Issue #6: No Graceful Shutdown Handler

### Description
When the gateway is stopped (Ctrl+C), there's no cleanup of resources or saving of state.

### Root Cause
Missing signal handlers for graceful shutdown.

### Solution
**File:** `c:\Users\nator\clawd\moltbot\gateway\server.py`

**Add shutdown handler in `__main__`:**

```python
if __name__ == "__main__":
    import signal
    
    gateway = MistGateway()
    
    def shutdown_handler(signum, frame):
        logger.info("Shutdown signal received - saving state...")
        gateway.save_history()
        logger.info("History saved. Goodbye! 🌙")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    try:
        asyncio.run(gateway.start())
    except KeyboardInterrupt:
        shutdown_handler(None, None)
```

---

## 🟢 Issue #7: Memory Truncation Too Aggressive

### Description
Long-term memory is truncated to 10,000 characters (line 696-697), which may lose important context.

### Root Cause
Arbitrary limit was set without considering actual token limits.

### Solution
**File:** `c:\Users\nator\clawd\moltbot\gateway\server.py`

**Implement smarter memory management:**

```python
async def process_llm_request(self, websocket, user_message, run_id, session_key: str):
    try:
        # Smarter memory truncation - prioritize recent entries
        memory_context = self._sanitize_memory(self.long_term_memory)
        
        # Calculate effective limit (Mistral context is ~8K tokens, ~4 chars/token)
        # Reserve ~4K for system prompt, history, and response
        MAX_MEMORY_CHARS = 16000  # ~4K tokens
        
        if len(memory_context) > MAX_MEMORY_CHARS:
            # Keep the identity section (first ~2000 chars) and most recent memories
            sections = memory_context.split("===")
            
            # Keep identity (first section)
            identity_section = sections[0] if sections else ""
            
            # Keep most recent from remaining
            remaining = "===".join(sections[1:]) if len(sections) > 1 else ""
            remaining_limit = MAX_MEMORY_CHARS - len(identity_section) - 100
            
            if len(remaining) > remaining_limit:
                remaining = "...(older memories truncated)...\n" + remaining[-remaining_limit:]
            
            memory_context = identity_section + "===" + remaining
        
        # ... rest of method
```

---

## 🚀 Quick Fix Script

Run this to apply the most critical fixes:

**File:** `c:\Users\nator\clawd\scripts\apply_critical_fixes.py`

```python
"""Apply critical fixes to the Clawd ecosystem."""
import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def fix_logging():
    """Add UTF-8 logging configuration."""
    print("✓ Logging fix requires manual edit to server.py")
    print("  See ISSUES_AND_SOLUTIONS.md Issue #1")

def ensure_openclaw_config():
    """Create default OpenClaw config if missing."""
    config_path = Path.home() / ".clawdbot" / "moltbot.json"
    
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            "tools": {
                "elevated": {
                    "enabled": True,
                    "allowList": ["read_file", "write_file", "list_dir", "cmd"]
                }
            },
            "channels": {"whatsapp": {"enabled": False}},
            "safety": {"blockedCommands": ["del /s", "rm -rf", "format"]}
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        print(f"✓ Created OpenClaw config: {config_path}")
    else:
        print(f"✓ OpenClaw config exists: {config_path}")

def ensure_directories():
    """Ensure all required directories exist."""
    dirs = [
        PROJECT_ROOT / "data",
        PROJECT_ROOT / "memory",
        PROJECT_ROOT / "logs",
        PROJECT_ROOT / "mycelium" / "data",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ready: {d}")

def main():
    print("=" * 50)
    print("Clawd Ecosystem - Critical Fixes")
    print("=" * 50)
    
    fix_logging()
    ensure_openclaw_config()
    ensure_directories()
    
    print("\n" + "=" * 50)
    print("Done! See ISSUES_AND_SOLUTIONS.md for remaining fixes.")
    print("=" * 50)

if __name__ == "__main__":
    main()
```

---

## 📊 Priority Matrix

```
                    IMPACT
              Low         High
         ┌──────────┬──────────┐
    Low  │  #4, #7  │    #3    │
EFFORT   ├──────────┼──────────┤
   High  │    #6    │  #1, #2  │
         └──────────┴──────────┘

Recommended Order: #1 → #5 → #2 → #3 → #6 → #4 → #7
```

---

## ✅ Verification Checklist

After applying fixes:

- [ ] Gateway starts without Unicode errors
- [ ] WebSocket connections remain stable for 10+ minutes
- [ ] Silence mode works when flag is set
- [ ] OpenClaw config exists and is loaded
- [ ] Graceful shutdown saves history
- [ ] Memory truncation preserves identity section

---

**Last Updated:** 2026-02-08
**Next Review:** After fixes applied
