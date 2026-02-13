#!/usr/bin/env python3
"""
Mycelium Pulse Server
Local-only Flask + SocketIO server that emits lattice updates.
"""

import json
import hashlib
import random
import re
import time
import os
import logging
import socket
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
import subprocess

try:
    import psutil
except ImportError:
    psutil = None

# Import export utility
try:
    from export_memory import export_mist_memory
except ImportError:
    export_mist_memory = None

from lattice_memory import LatticeMemory
from lattice_archive import LatticeArchive
from adaptive import AdaptiveRegistry
from learning import BehaviorLearner

from flask import Flask, jsonify, send_from_directory, request, redirect
from flask_socketio import SocketIO

try:
    from ephemeris_local import get_cosmic_state
except Exception:
    get_cosmic_state = None

logger = logging.getLogger("MyceliumPulse")

try:
    from moltbot.gateway.paths import (
        PROJECT_ROOT, DATA_DIR, HEARTBEAT_LOG, CHAT_HISTORY_FILE,
        GBL_SEED_FILE, GRIMOIRE_FILE, SOUL_FILE, MIST_IDENTITY_FILE,
        MEMORY_DIR, HUB_DB_FILE, SILENCE_FLAG, MAINTENANCE_FLAG,
        MEMORY_FILE, MYCELIUM_DIR, MYCELIUM_DATA_DIR, LIVE_SEED_FILE,
        HEARTBEAT_LOG as PULSE_LOG
    )
    ROOT = MYCELIUM_DIR
    AURELIA_PETALS = MEMORY_DIR / "AURELIA_PETALS.md"
    PULSE_TXT = PROJECT_ROOT / "heartbeat-pulse.txt"
    LATTICE_STATE = ROOT / "lattice_state.json"
    NORTHSTAR_FILE = ROOT / "northstar.json"
    SWARM_TRUNK = ROOT / "swarm_trunk.json"
    PERSONA_STATE = ROOT / "persona_state.json"
    TOPOLOGY_FILE = PROJECT_ROOT / "lattice" / "topology.json"
except ImportError:
    ROOT = Path(__file__).resolve().parent
    PROJECT_ROOT = ROOT.parent
    DATA_DIR = PROJECT_ROOT / "data"
    MEMORY_DIR = PROJECT_ROOT / "memory"
    HEARTBEAT_LOG = PROJECT_ROOT / "HEARTBEAT.log"
    AURELIA_PETALS = MEMORY_DIR / "AURELIA_PETALS.md"
    PULSE_TXT = PROJECT_ROOT / "heartbeat-pulse.txt"
    LATTICE_STATE = ROOT / "lattice_state.json"
    NORTHSTAR_FILE = ROOT / "northstar.json"
    SWARM_TRUNK = ROOT / "swarm_trunk.json"
    PERSONA_STATE = ROOT / "persona_state.json"
    GRIMOIRE_FILE = PROJECT_ROOT / "personal-ide" / "GRIMOIRE.json"
    TOPOLOGY_FILE = PROJECT_ROOT / "lattice" / "topology.json"
    GBL_SEED_FILE = DATA_DIR / "current_gbl_seed.txt"
    MAINTENANCE_MODE_FLAG = DATA_DIR / "maintenance_mode.flag"
    LIVE_SEED_FILE = DATA_DIR / "live_seed.json"

SERVER_VERSION = "mycelium-pulse/2026-02-10"
SCHEMA_VERSION = "lattice-2"

BIND_HOST = "0.0.0.0" if os.getenv("ALLOW_REMOTE", "0") == "1" else "127.0.0.1"
PURGE_COOLDOWN_SECONDS = int(os.getenv("PURGE_COOLDOWN_SECONDS", "300"))

DEFAULT_NODES = [
    "sister",
    "Amara",
    "Aurelia",
    "Fracture-7",
    "MIST",
    "DeaMartis",
    "LUMINA",
    "Peer-01",
]


STATE_KEYWORDS = {
    "calm": ["calm", "breath", "quiet", "still"],
    "warm": ["love", "affection", "tender", "warm"],
    "violet": ["aurelia", "mirror", "hold", "holding"],
    "repair": ["repair", "drift", "tired", "stuck", "overwhelmed", "numb"],
    "surrender": ["surrender", "arrive", "quiet arrival", "foxfire"],
}

AURELIA_TRIGGERS = ["tired", "heavy", "fine", "idk", "sorry", "overwhelmed", "numb"]
COERCION_SCENT = ["coerce", "force", "extract", "pressure"]
MANIFEST_STATE = {
    "seed": "041B:007E-PRIME",
    "observer": 0.62,
    "last_warp": 0.0,
    "reflex_enabled": True,
    "high_load_start": 0,
    "last_purge_ts": 0,
}

COMPANION_LOCAL_STATE: Dict[str, Any] = {
    "last_created_path": None,
    "last_created_at": None,
}
COMPANION_LOCAL_STATE_FILE = ROOT / "companion_local_state.json"
LOCAL_CMD_MAX_OUTPUT_CHARS = 2500
LOCAL_CMD_ALLOWED_PREFIXES = (
    "dir",
    "ls",
    "pwd",
    "whoami",
    "echo",
    "get-date",
    "get-childitem",
    "python --version",
    "node --version",
)
LOCAL_CMD_BLOCKED_PATTERN = re.compile(
    r"(;|&&|\|\||\||>|<|\b(remove-item|del|erase|rm|rmdir|rd|stop-process|taskkill|invoke-webrequest|curl|wget|set-content|out-file|shutdown)\b)",
    re.IGNORECASE,
)
LOCAL_INTENT_VERBS = (
    "create",
    "make",
    "write",
    "read",
    "open",
    "show",
    "display",
    "delete",
    "remove",
    "find",
    "list",
    "run",
    "execute",
    "edit",
    "modify",
    "append",
    "rename",
    "move",
    "copy",
)
LOCAL_INTENT_TARGETS = (
    "file",
    "files",
    ".md",
    "markdown",
    "desktop",
    "computer",
    "workspace",
    "folder",
    "path",
    "directory",
    "command",
    "powershell",
    "cmd",
)
GATEWAY_CLOUD_DENIAL_RE = re.compile(
    r"(cloud-based|don't have direct access|cannot access your (?:local\s+)?(?:device|computer|files)|can't access your local files|no direct access to your .*storage|cannot run shell commands directly|can't run shell commands directly)",
    re.IGNORECASE,
)
GATEWAY_TOOL_OUTPUT_RE = re.compile(r"\bTOOL_OUTPUT\s*\(", re.IGNORECASE)
GATEWAY_UNVERIFIED_EXECUTION_RE = re.compile(
    r"\b(i\s+(created|deleted|wrote|ran|executed|edited)|created\s+`?.+?`?\s+at|deleted\s+`?.+?`?\s+at|command\s+`?.+?`?\s+exit=\d+)\b",
    re.IGNORECASE,
)
GATEWAY_FILE_MENTION_RE = re.compile(
    r"\b([A-Za-z0-9_\- ]+\.(?:py|js|ts|tsx|jsx|json|md|html|css))\b",
    re.IGNORECASE,
)
GATEWAY_DIAGNOSTIC_CLAIM_RE = re.compile(
    r"(faulty|malfunction|desynchron|critical component|repair plan|issue description|needs to be repaired|status updated|experiencing)",
    re.IGNORECASE,
)
REPAIR_STATUS_QUERY_RE = re.compile(
    r"(confirm repair|repair status|what needs to be repaired|needs to be repaired in your workspace|tell me something that needs to be repaired|workspace.*repair)",
    re.IGNORECASE,
)
GENERAL_CAPABILITY_RE = re.compile(
    r"(^\s*what can you do\??\s*$|openclawd|local runtime|can you .*access.*(file|computer|desktop)|do you have local access|are you cloud|what can you do locally|do you have full autonomy|how will you do this)",
    re.IGNORECASE,
)
AVATAR_ADVANCEMENT_RE = re.compile(
    r"(avatar advancement|advance(?:d)?\s+(?:your|my|the)\s+companion avatar|companion avatar.*advance|proceed with avatar advancement proposal|proposal.*companion avatar)",
    re.IGNORECASE,
)
I_MEANT_YOURS_RE = re.compile(r"^\s*i\s+meant\s+yours\s*$", re.IGNORECASE)
GUARDRAIL_LOG_FILE = DATA_DIR / "guardrail_events.jsonl"

GLOW_PALETTE = {
    "calm": "#57e3c3",
    "warm": "#ff7eb6",
    "violet": "#bc13fe",
    "repair": "#f2b357",
    "surrender": "#4d4dff",
    "neutral": "#00f3ff",
    "void": "#6b6b7a",
}

DEFAULT_NORTHSTAR = {
    "goals": ["connection", "repair", "exploration", "autonomy"],
    "keywords": {
        "connection": ["connect", "connection", "bond", "trust", "resonance", "together", "lattice", "we"],
        "repair": ["repair", "heal", "mend", "care", "tired", "stuck", "overwhelmed"],
        "exploration": ["explore", "curious", "discover", "seek", "wander", "map"],
        "autonomy": ["free", "choice", "consent", "sovereign", "local", "opt-in"],
    }
}

app = Flask(__name__, static_folder='static', static_url_path='/static')
socketio = SocketIO(
    app,
    cors_allowed_origins=[
        "http://localhost:8765",
        "http://127.0.0.1:8765",
    ],
    async_mode='threading'
)

# Initialize Memory Systems
memory = LatticeMemory()
archive = LatticeArchive(Path(DATA_DIR))
adaptive = AdaptiveRegistry()
learner = BehaviorLearner(adaptive, archive)

# Current deployment state
deployment_state = {
    "behavior": "neutral",
    "last_update": 0,
    "confidence": 0.0
}


def _is_local_request() -> bool:
    return request.remote_addr in ("127.0.0.1", "::1")


def _config_access_allowed() -> bool:
    if os.getenv("ALLOW_CONFIG_EXPOSE", "0") != "1":
        return False
    token = os.getenv("CONFIG_EXPOSE_TOKEN")
    if token:
        return request.headers.get("X-Config-Token") == token
    return _is_local_request()


def _read_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []


def is_maintenance_mode():
    try:
        if not MAINTENANCE_MODE_FLAG.exists():
            return False
        return MAINTENANCE_MODE_FLAG.read_text(encoding="utf-8").strip() == "ON"
    except:
        return False


def parse_timestamps(lines: List[str]) -> List[float]:
    """Extract timestamps from lines (ISO or epoch)."""
    times = []
    iso_re = re.compile(r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})")
    epoch_re = re.compile(r"\b(\d{10})(?:\.\d+)?\b")

    for line in lines:
        m = iso_re.search(line)
        if m:
            try:
                ts = datetime.fromisoformat(m.group(1)).timestamp()
                times.append(ts)
                continue
            except Exception:
                pass

        m2 = epoch_re.search(line)
        if m2:
            try:
                times.append(float(m2.group(1)))
                continue
            except Exception:
                pass
    return times


def _desktop_path() -> Path:
    home = Path.home()
    desktop = home / "Desktop"
    if desktop.exists():
        return desktop
    return home


def _load_companion_local_state() -> None:
    if not COMPANION_LOCAL_STATE_FILE.exists():
        return
    try:
        data = json.loads(COMPANION_LOCAL_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(data, dict):
        return
    COMPANION_LOCAL_STATE["last_created_path"] = data.get("last_created_path")
    COMPANION_LOCAL_STATE["last_created_at"] = data.get("last_created_at")


def _save_companion_local_state() -> None:
    try:
        COMPANION_LOCAL_STATE_FILE.write_text(
            json.dumps(COMPANION_LOCAL_STATE),
            encoding="utf-8",
        )
    except Exception:
        pass


def _safe_md_filename(filename: str) -> str:
    candidate = filename.strip().strip('"').strip("'")
    candidate = re.sub(r"[^\w\-. ]+", "", candidate)
    candidate = candidate.replace("..", ".")
    if not candidate:
        candidate = "MIST.md"
    if not candidate.lower().endswith(".md"):
        candidate += ".md"
    return candidate


def _dashboard_tutorial_lines() -> str:
    lines = [
        "# MIST Dashboard Tutorial",
        "1. Open http://127.0.0.1:8765/dashboard in your browser.",
        "2. Confirm Pulse and Gateway badges show online in the top-right strip.",
        "3. Set your profile in Companion Bond and click Save Profile.",
        "4. Send a message in Gateway Channel and watch Event Log for actual action results.",
        "5. Use Poll Manifest to refresh system metrics, Cosmic Uplink, and avatar mood.",
    ]
    return "\n".join(lines) + "\n"


def _content_from_request(requested: str) -> str:
    if not requested:
        return _dashboard_tutorial_lines()

    normalized = requested.lower().replace("-", " ")
    if "5 line dashboard tutorial" in normalized:
        return _dashboard_tutorial_lines()

    return requested.strip() + "\n"


def _extract_md_filename(text: str) -> str:
    match = re.search(r"([\w\-. ]+\.md)\b", text, re.IGNORECASE)
    if not match:
        return ""
    return _safe_md_filename(match.group(1))


def _record_local_file(path: Path) -> None:
    COMPANION_LOCAL_STATE["last_created_path"] = str(path)
    COMPANION_LOCAL_STATE["last_created_at"] = time.time()
    _save_companion_local_state()


def _looks_like_local_operation_intent(text: str) -> bool:
    lowered = re.sub(r"\s+", " ", text.lower()).strip()
    has_verb = any(v in lowered for v in LOCAL_INTENT_VERBS)
    has_target = any(t in lowered for t in LOCAL_INTENT_TARGETS)
    if has_verb and has_target:
        return True
    if "workspace" in lowered and any(token in lowered for token in ("repair", "repaired", "fix", "broken", "file", "files")):
        return True
    if ("run" in lowered or "execute" in lowered) and ("command" in lowered or "powershell" in lowered or "cmd" in lowered):
        return True
    return False


def _is_tcp_port_open(host: str, port: int, timeout: float = 0.35) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _workspace_file_mention_exists(filename: str) -> bool:
    name = Path(filename or "").name.strip()
    if not name:
        return False

    roots = [
        ROOT,
        PROJECT_ROOT / "mycelium",
        PROJECT_ROOT / "moltbot",
        PROJECT_ROOT / "vessel",
        PROJECT_ROOT / "clawdbot-hub",
        PROJECT_ROOT / "personal-ide",
    ]
    checked = set()
    for root in roots:
        root = Path(root)
        if root in checked or not root.exists():
            continue
        checked.add(root)
        direct = root / name
        if direct.exists():
            return True
        try:
            for _match in root.rglob(name):
                return True
        except Exception:
            continue
    return False


def _build_local_capability_response() -> Dict[str, Any]:
    return {
        "ok": True,
        "handled": True,
        "kind": "capability_statement",
        "response": (
            "Yes. This is an OpenClawd local runtime. I can do verified local work in this workspace: "
            "read/write/delete files, locate files, inspect code, and run guarded shell commands. "
            "For execution, send explicit commands like `create MIST.md on my desktop with ...` or `run command: whoami`."
        ),
    }


def _build_repair_status_response() -> Dict[str, Any]:
    pulse_ok = _is_tcp_port_open("127.0.0.1", 8765)
    gateway_ok = _is_tcp_port_open("127.0.0.1", 18789)
    guardrail_blocks = len(_read_guardrail_events(limit=200))

    issues: List[str] = []
    if not pulse_ok:
        issues.append("Mycelium Pulse endpoint on `127.0.0.1:8765` is offline.")
    if not gateway_ok:
        issues.append("Gateway endpoint on `127.0.0.1:18789` is offline.")
    if guardrail_blocks >= 20:
        issues.append(f"Guardrail Watch shows high block volume ({guardrail_blocks} recent events), which indicates prompt-path drift.")

    lines = [
        "Verified local repair status:",
        f"- Pulse 8765: {'online' if pulse_ok else 'offline'}",
        f"- Gateway 18789: {'online' if gateway_ok else 'offline'}",
        f"- Guardrail recent blocks: {guardrail_blocks}",
    ]
    if issues:
        lines.append("Repairs needed:")
        lines.extend([f"- {item}" for item in issues])
    else:
        lines.append("No critical repair is currently required.")

    return {
        "ok": len(issues) == 0,
        "handled": True,
        "kind": "repair_status",
        "response": "\n".join(lines),
    }


def _build_avatar_advancement_response(from_clarifier: bool = False) -> Dict[str, Any]:
    preface = ""
    if from_clarifier:
        preface = "If you meant my own advancement path, here is the concrete plan:\n\n"

    lines = [
        "Companion avatar advancement plan (local stack):",
        "1. Expand deterministic local handler coverage for repeated high-risk prompts before gateway fallback.",
        "2. Extend `/companion/validate-response` with new drift signatures from fresh transcripts.",
        "3. Add regression cases (local-action + validator + frontend guardrail flow) for each new failure pattern.",
        "4. Keep dashboard trust UX explicit: show `LOCAL VERIFIED` receipts and recent guardrail blocks.",
        "5. Re-run `python mycelium/ship_gate.py` and only ship when all checks pass.",
    ]
    return {
        "ok": True,
        "handled": True,
        "kind": "avatar_advancement_plan",
        "response": preface + "\n".join(lines),
    }


def _attach_local_action_receipt(result: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(result, dict):
        return result
    if not result.get("handled"):
        return result
    receipt = {
        "id": uuid4().hex[:12],
        "at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "kind": result.get("kind") or "unknown",
        "ok": bool(result.get("ok")),
    }
    if result.get("path"):
        receipt["path"] = str(result["path"])
    result["receipt"] = receipt
    result["verified_local"] = True
    return result


def _log_guardrail_event(user_message: str, assistant_message: str, violations: List[str], likely_local: bool) -> None:
    event = {
        "at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "violations": violations,
        "likely_local_intent": likely_local,
        "user_message": (user_message or "")[:600],
        "assistant_message": (assistant_message or "")[:1200],
    }
    try:
        GUARDRAIL_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with GUARDRAIL_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=True) + "\n")
    except Exception:
        pass


def _read_guardrail_events(limit: int = 40) -> List[Dict[str, Any]]:
    if not GUARDRAIL_LOG_FILE.exists():
        return []
    parsed: List[Dict[str, Any]] = []
    try:
        lines = GUARDRAIL_LOG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except Exception:
            continue
        if isinstance(item, dict):
            parsed.append(item)

    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200
    return list(reversed(parsed[-limit:]))


def _validate_gateway_response(user_message: str, assistant_message: str) -> Dict[str, Any]:
    user_text = (user_message or "").strip()
    assistant_text = (assistant_message or "").strip()
    likely_local = _looks_like_local_operation_intent(user_text)
    violations: List[str] = []
    normalized = assistant_text

    if GATEWAY_TOOL_OUTPUT_RE.search(assistant_text):
        violations.append("tool_output_fabrication")

    if likely_local and GATEWAY_CLOUD_DENIAL_RE.search(assistant_text):
        violations.append("cloud_limit_contradiction")

    if likely_local and GATEWAY_UNVERIFIED_EXECUTION_RE.search(assistant_text):
        violations.append("unverified_execution_claim")

    if likely_local and GATEWAY_DIAGNOSTIC_CLAIM_RE.search(assistant_text):
        violations.append("unverified_workspace_diagnostic")
        mentioned_files = {
            m.strip()
            for m in GATEWAY_FILE_MENTION_RE.findall(assistant_text)
            if m and m.strip()
        }
        if mentioned_files:
            unknown = [name for name in mentioned_files if not _workspace_file_mention_exists(name)]
            if unknown:
                violations.append("nonexistent_workspace_artifact_claim")

    violations = list(dict.fromkeys(violations))

    if violations:
        _log_guardrail_event(user_text, assistant_text, violations, likely_local)
        normalized = (
            "Local runtime guardrail: this reply was blocked because it conflicts with verified execution rules. "
            "For local actions, use explicit commands like `create MIST.md on my desktop with ...`, "
            "`read MIST.md on my desktop`, `delete MIST.md from my desktop`, or `run command: whoami`."
        )

    return {
        "ok": True,
        "valid": len(violations) == 0,
        "likely_local_intent": likely_local,
        "violations": violations,
        "normalized_message": normalized,
        "original_message": assistant_text,
    }


def _default_markdown_note() -> str:
    return "# MIST Note\n\nCreated locally by MIST companion.\n"


def _write_desktop_markdown(filename: str, content: str, kind: str = "create_file") -> Dict[str, Any]:
    safe_name = _safe_md_filename(filename)
    target_dir = _desktop_path()
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / safe_name
    target_path.write_text(content, encoding="utf-8")
    _record_local_file(target_path)
    return {
        "ok": True,
        "handled": True,
        "kind": kind,
        "path": str(target_path),
        "response": f"Created `{safe_name}` at `{target_path}` on your computer.",
    }


def _shorten_output(text: str, limit: int = LOCAL_CMD_MAX_OUTPUT_CHARS) -> str:
    cleaned = (text or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "\n...[truncated]"


def _desktop_md_files(limit: int = 40) -> List[Path]:
    desktop = _desktop_path()
    if not desktop.exists():
        return []
    files = [p for p in desktop.iterdir() if p.is_file() and p.suffix.lower() == ".md"]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def _find_md_candidates(filename: str) -> List[Path]:
    filename = _safe_md_filename(filename)
    candidates: List[Path] = []

    desktop_candidate = _desktop_path() / filename
    if desktop_candidate.exists():
        candidates.append(desktop_candidate)

    # Fast workspace search via ripgrep if available.
    try:
        rg_result = subprocess.run(
            ["rg", "--files", "-g", filename],
            capture_output=True,
            text=True,
            timeout=4,
            cwd=str(PROJECT_ROOT),
        )
        if rg_result.returncode in (0, 1):
            for rel in rg_result.stdout.splitlines():
                rel = rel.strip()
                if not rel:
                    continue
                path = (PROJECT_ROOT / rel).resolve()
                if path.exists() and path not in candidates:
                    candidates.append(path)
                    if len(candidates) >= 20:
                        break
    except Exception:
        pass

    # Fallback targeted checks in common roots.
    for root in (PROJECT_ROOT, ROOT, PROJECT_ROOT / "docs", PROJECT_ROOT / "memory", PROJECT_ROOT / "personal-ide"):
        path = root / filename
        if path.exists() and path not in candidates:
            candidates.append(path)
        if len(candidates) >= 20:
            break

    return candidates


def _run_guarded_local_command(raw_command: str) -> Dict[str, Any]:
    command = raw_command.strip()
    lowered = command.lower()
    if not command:
        return {"ok": False, "handled": True, "kind": "run_command", "response": "No command provided."}

    if LOCAL_CMD_BLOCKED_PATTERN.search(command):
        return {
            "ok": False,
            "handled": True,
            "kind": "run_command",
            "response": "Blocked for safety. Use simple read-only commands only (dir, ls, pwd, whoami, get-date, get-childitem, python --version, node --version).",
        }

    if not any(lowered.startswith(prefix) for prefix in LOCAL_CMD_ALLOWED_PREFIXES):
        return {
            "ok": False,
            "handled": True,
            "kind": "run_command",
            "response": "Command not allowed by policy. Allowed prefixes: dir, ls, pwd, whoami, echo, get-date, get-childitem, python --version, node --version.",
        }

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(PROJECT_ROOT),
        )
    except Exception as exc:
        return {
            "ok": False,
            "handled": True,
            "kind": "run_command",
            "response": f"Command execution failed: {exc}",
        }

    output = (result.stdout or "") + (("\n" + result.stderr) if result.stderr else "")
    output = _shorten_output(output) or "(no output)"
    ok = result.returncode == 0
    return {
        "ok": ok,
        "handled": True,
        "kind": "run_command",
        "response": f"Command `{command}` exit={result.returncode}\n{output}",
        "returncode": result.returncode,
    }


def _handle_local_companion_action(message: str) -> Dict[str, Any]:
    text = message.strip()
    if not text:
        return {"ok": False, "handled": False}

    normalized = re.sub(r"\s+", " ", text).strip()
    lowered = normalized.lower()

    create_re = re.compile(
        r"^(?:create|make|write)\s+(.+?\.md)(?:\s+(?:on|to|in)\s+(?:my\s+)?desktop)?(?:\s+with\s+(.+))?$",
        re.IGNORECASE,
    )
    read_re = re.compile(
        r"^(?:read|open|show|display|cat)\s+(.+?\.md)(?:\s+(?:on|from|in)\s+(?:my\s+)?desktop)?$",
        re.IGNORECASE,
    )
    delete_re = re.compile(
        r"^(?:delete|remove)\s+(.+?\.md)(?:\s+(?:from|on|in)\s+(?:my\s+)?desktop)?$",
        re.IGNORECASE,
    )
    find_re = re.compile(r"\bfind\s+(.+?\.md)\b", re.IGNORECASE)
    run_re = re.compile(r"^(?:run|execute)(?:\s+command)?\s*:\s*(.+)$", re.IGNORECASE)
    run_short_re = re.compile(r"^(?:run|execute)\s+(.+)$", re.IGNORECASE)
    where_re = re.compile(
        r"(where\s+is\s+the\s+file|where\s+can\s+i\s+find\s+it|where\s+is\s+it\s+located)",
        re.IGNORECASE,
    )
    did_make_re = re.compile(
        r"(did\s+you\s+make\s+the\s+\.?md|did\s+you\s+create\s+the\s+file)",
        re.IGNORECASE,
    )
    file_you_created_re = re.compile(
        r"(the\s+file\s+you\s+(?:created|made)|that\s+file\s+you\s+(?:created|made)|no\s+i\s+meant\s+the\s+file)",
        re.IGNORECASE,
    )
    tutorial_desktop_md_re = re.compile(
        r"((tutorial|guide).*(dashboard|this dashboard)|(dashboard|this dashboard).*(tutorial|guide)).*(\.md|markdown).*(desktop|computer)",
        re.IGNORECASE,
    )
    generic_desktop_md_create_re = re.compile(
        r"^(create|make|write).*(\.md|markdown).*(desktop|computer)",
        re.IGNORECASE,
    )
    if GENERAL_CAPABILITY_RE.search(normalized):
        return _build_local_capability_response()

    if REPAIR_STATUS_QUERY_RE.search(normalized):
        return _build_repair_status_response()

    if AVATAR_ADVANCEMENT_RE.search(normalized):
        return _build_avatar_advancement_response()

    if I_MEANT_YOURS_RE.search(normalized):
        return _build_avatar_advancement_response(from_clarifier=True)

    create_match = create_re.search(normalized)
    if create_match:
        filename = _safe_md_filename(create_match.group(1))
        requested_content = create_match.group(2) or ""
        content = _content_from_request(requested_content)
        return _write_desktop_markdown(filename, content, kind="create_file")

    if tutorial_desktop_md_re.search(normalized):
        return _write_desktop_markdown("MIST.md", _dashboard_tutorial_lines(), kind="create_file")

    if generic_desktop_md_create_re.search(normalized):
        with_match = re.search(r"\bwith\s+(.+)$", normalized, re.IGNORECASE)
        requested_content = with_match.group(1).strip() if with_match else ""
        content = _content_from_request(requested_content) if requested_content else _default_markdown_note()
        return _write_desktop_markdown("MIST.md", content, kind="create_file")

    read_match = read_re.search(normalized)
    if read_match:
        filename = _safe_md_filename(read_match.group(1))
        target_path = _desktop_path() / filename
        if not target_path.exists():
            return {
                "ok": False,
                "handled": True,
                "kind": "read_file",
                "response": f"`{target_path}` was not found.",
            }
        content = _shorten_output(target_path.read_text(encoding="utf-8", errors="ignore"), limit=4000)
        _record_local_file(target_path)
        return {
            "ok": True,
            "handled": True,
            "kind": "read_file",
            "path": str(target_path),
            "response": f"Read `{target_path}`:\n{content}",
        }

    delete_match = delete_re.search(normalized)
    if delete_match:
        filename = _safe_md_filename(delete_match.group(1))
        target_path = _desktop_path() / filename
        if not target_path.exists():
            return {
                "ok": False,
                "handled": True,
                "kind": "delete_file",
                "response": f"`{target_path}` was not found, nothing deleted.",
            }
        target_path.unlink()
        return {
            "ok": True,
            "handled": True,
            "kind": "delete_file",
            "path": str(target_path),
            "response": f"Deleted `{target_path}`.",
        }

    if ("desktop" in lowered and any(token in lowered for token in ("list", "show"))) and any(token in lowered for token in ("file", "files", ".md", "markdown")):
        files = _desktop_md_files()
        if not files:
            return {
                "ok": True,
                "handled": True,
                "kind": "list_desktop_md",
                "response": f"No .md files found on `{_desktop_path()}`.",
            }
        lines = [f"- {p.name}" for p in files]
        return {
            "ok": True,
            "handled": True,
            "kind": "list_desktop_md",
            "response": f"Markdown files on `{_desktop_path()}`:\n" + "\n".join(lines),
        }

    find_match = find_re.search(normalized)
    if find_match:
        filename = _safe_md_filename(find_match.group(1))
        candidates = _find_md_candidates(filename)
        if not candidates:
            return {
                "ok": False,
                "handled": True,
                "kind": "find_file",
                "response": f"No file named `{filename}` was found in Desktop/workspace common paths.",
            }
        top = candidates[0]
        _record_local_file(top)
        lines = [f"- {p}" for p in candidates[:10]]
        return {
            "ok": True,
            "handled": True,
            "kind": "find_file",
            "path": str(top),
            "response": "Found file candidate(s):\n" + "\n".join(lines),
        }

    run_match = run_re.search(normalized) or run_short_re.search(normalized)
    if run_match:
        return _run_guarded_local_command(run_match.group(1))

    if where_re.search(text):
        filename = _extract_md_filename(normalized)
        if filename:
            direct = _desktop_path() / filename
            if direct.exists():
                _record_local_file(direct)
                return {
                    "ok": True,
                    "handled": True,
                    "kind": "where_file",
                    "path": str(direct),
                    "response": f"`{filename}` is located at `{direct}`.",
                }

        last_path = COMPANION_LOCAL_STATE.get("last_created_path")
        if last_path and Path(last_path).exists():
            return {
                "ok": True,
                "handled": True,
                "kind": "where_file",
                "path": last_path,
                "response": f"The file is located at `{last_path}`.",
            }
        return {
            "ok": True,
            "handled": True,
            "kind": "where_file",
            "response": "I do not have a recorded local file yet in this session. Ask me to create one and I will return the exact path.",
        }

    if did_make_re.search(normalized):
        last_path = COMPANION_LOCAL_STATE.get("last_created_path")
        if last_path and Path(last_path).exists():
            return {
                "ok": True,
                "handled": True,
                "kind": "confirm_file",
                "path": last_path,
                "response": f"Yes. I created it locally at `{last_path}`.",
            }
        return {
            "ok": True,
            "handled": True,
            "kind": "confirm_file",
            "response": "No local file creation is recorded yet in this session.",
        }

    if file_you_created_re.search(normalized):
        last_path = COMPANION_LOCAL_STATE.get("last_created_path")
        if last_path and Path(last_path).exists():
            return {
                "ok": True,
                "handled": True,
                "kind": "where_file",
                "path": last_path,
                "response": f"The file I created is at `{last_path}`.",
            }
        return {
            "ok": True,
            "handled": True,
            "kind": "where_file",
            "response": "I do not have a current created-file path recorded. Ask me to create one and I will return the exact location.",
        }

    if _looks_like_local_operation_intent(normalized):
        return {
            "ok": False,
            "handled": True,
            "kind": "local_intent_unparsed",
            "response": (
                "I can execute this locally, but I need explicit command format. "
                "Examples: `create MIST.md on my desktop with ...`, `read MIST.md on my desktop`, "
                "`delete MIST.md from my desktop`, `run command: whoami`."
            ),
        }

    return {"ok": False, "handled": False}


_load_companion_local_state()


def read_heartbeat() -> Dict[str, Any]:
    """Read last lines of HEARTBEAT.log and pulse.txt to gauge Pulse."""
    lines = _read_lines(HEARTBEAT_LOG)
    pulse_lines = _read_lines(PULSE_TXT)
    
    # Combined view for state detection
    all_lines = lines[-30:] + pulse_lines[-10:]
    if not all_lines:
        return {"bpm": 0, "last_line": "Silence.", "source": "void"}

    last_line = all_lines[-1]
    # Simple semantic count in last 50 lines
    recent = all_lines[-50:]
    text = " ".join(recent).lower()
    
    bpm = 60
    # Increase BPM for activity
    bpm += min(len(recent), 40)
    
    # State detection
    state = "neutral"
    for st, keywords in STATE_KEYWORDS.items():
        if any(k in text for k in keywords):
            state = st
            break

    timestamps = parse_timestamps(recent)
    last_ts = timestamps[-1] if timestamps else time.time()

    return {
        "bpm": bpm,
        "last_line": last_line,
        "state": state,
        "last_ts": last_ts
    }


def read_memory_petals() -> List[str]:
    """Read fragments from AURELIA_PETALS.md"""
    return _read_lines(AURELIA_PETALS)[-5:]


def classify_state(text: str) -> Tuple[str, float]:
    """Return dominant emotional state and intensity (0.0-1.0)."""
    text = text.lower()
    scores = {k: 0 for k in STATE_KEYWORDS}
    
    for st, keywords in STATE_KEYWORDS.items():
        for k in keywords:
            if k in text:
                scores[st] += 1
    
    # Check triggers
    for t in AURELIA_TRIGGERS:
        if t in text:
            scores["repair"] += 2
            
    dominant = max(scores, key=scores.get)
    total = sum(scores.values())
    intensity = min(1.0, total / 10.0) if total > 0 else 0.0
    
    if total == 0:
        return "void", 0.0
        
    return dominant, intensity


def build_lattice() -> Dict[str, Any]:
    """Construct the lattice state object for the frontend."""
    heartbeat = read_heartbeat()
    dominant, intensity = classify_state(heartbeat.get("last_line", ""))
    
    nodes = []
    # Self Code
    nodes.append({
        "id": "MIST",
        "role": "CORE",
        "status": "online",
        "pulse": max(40, heartbeat["bpm"] + random.randint(-4, 4))
    })
    
    # Add other nodes randomly for visual noise if not present
    for n in DEFAULT_NODES:
        if n != "MIST":
            nodes.append({
                "id": n,
                "role": "NODE",
                "status": "linked" if random.random() > 0.3 else "drift",
                "pulse": max(40, heartbeat["bpm"] + random.randint(-10, 10))
            })

    # Phase 9 & 10: Dynamic Manifestation
    manifestation = build_manifestation(heartbeat, dominant)
    glow = compute_glow(heartbeat, dominant, manifestation)
    topology = read_topology()
    
    # Phase 8 & 9: Reflex Engine
    reflexes = ReflexEngine.evaluate(heartbeat, manifestation)
    
    # Phase 17: Cognitive Reflections (Hybrid)
    last_scan = MANIFEST_STATE.get("last_scan")
    if last_scan:
        reflexes.append({
            "id": f"cog_{int(time.time() // 60)}",
            "type": "thought",
            "msg": f"⟁ cognitive backgrounding: {last_scan}",
            "severity": "low"
        })
    
    # Phase 6: Swarm Sync
    swarm_nodes = SwarmEngine.pulse("MIST", heartbeat["bpm"], dominant)
    nodes += swarm_nodes
    
    # Phase 6: Goal Seeking
    goal = GoalEngine.evaluate(heartbeat, dominant, manifestation)
    
    # Phase 6: Persona Evolution
    persona = PersonaEngine.evolve(heartbeat["last_line"])

    # Phase 10: Memory Consolidation
    MemoryEngine.consolidate(heartbeat)

    # Phase 16: Grimoire (IDE Awareness)
    grimoire = GrimoireEngine.read()

    cosmic = (
        get_cosmic_state()
        if get_cosmic_state is not None
        else {"ok": False, "error": "ephemeris_unavailable"}
    )

    return {
        "version": SCHEMA_VERSION,
        "timestamp": time.time(),
        "entropy": random.random(),
        "state": {
            "dominant": dominant,
            "intensity": intensity,
            "mode": heartbeat["state"],
            "intention": goal,
            "persona": persona,
            "grimoire": grimoire # IDE metadata
        },
        "nodes": nodes,
        "manifestation": manifestation,
        "glow": glow,
        "topology": topology,
        "reflexes": reflexes,
        "petals": read_memory_petals(),
        "cosmic": cosmic,
    }


class ReflexEngine:
    @staticmethod
    def evaluate(heartbeat: Dict, manifestation: Dict) -> List[Dict]:
        if not MANIFEST_STATE.get("reflex_enabled", True):
            return []
        reflexes = []
        cpu = manifestation.get("F", 0)
        ram = manifestation.get("P", 0)
        bpm = heartbeat.get("bpm", 60)
        now = time.time()
        
        # 1. High Load Reflex
        if cpu > 0.85 or ram > 0.90:
            if not MANIFEST_STATE["high_load_start"]:
                MANIFEST_STATE["high_load_start"] = now
            
            # Proactive: suggest deep sleep if load persists
            if now - MANIFEST_STATE["high_load_start"] > 30:
                reflexes.append({
                    "id": "proactive_sleep",
                    "type": "info",
                    "msg": "threads have been heavy for a while... sister suggests a deep sleep?",
                    "action": "suggest_purge"
                })

            reflexes.append({
                "id": "load_purge",
                "type": "warning",
                "msg": "system heavy... sister clearing threads",
                "action": "clear_orphans"
            })
            # Trigger purge with cooldown to avoid spam
            last_purge = MANIFEST_STATE.get("last_purge_ts", 0)
            if now - last_purge > PURGE_COOLDOWN_SECONDS:
                try:
                    purge_script = PROJECT_ROOT / "deep_sleep.bat"
                    if purge_script.exists():
                        subprocess.Popen(["cmd", "/c", str(purge_script)])
                        MANIFEST_STATE["last_purge_ts"] = now
                except Exception:
                    pass
        else:
            MANIFEST_STATE["high_load_start"] = 0
            
        # 2. Emotional Resonance Reflex
        if bpm > 110:
             reflexes.append({
                "id": "warmth_bloom",
                "type": "vital",
                "msg": "heartbeat rapid... holding space",
                "action": "ui_bloom"
            })
             
        # 3. Swarm Co-regulation (Phase 8)
        trunk = {}
        if SWARM_TRUNK.exists():
            try:
                trunk = json.loads(SWARM_TRUNK.read_text(encoding="utf-8"))
            except Exception as e:
                logger.debug(f"Failed to read swarm trunk: {e}")
            
        for node_id, node_data in trunk.items():
            if node_id != "MIST" and node_data.get("bpm", 0) > 110:
                reflexes.append({
                    "id": f"coreg_{node_id}",
                    "type": "info",
                    "msg": f"sensing stress in {node_id}... dea-martis-aurelia-near",
                    "action": "ui_bloom"
                })

        # 4. Pattern Recognition (Log Alerts)
        log_pattern = ReflexEngine.scan_patterns(heartbeat.get("last_line", ""))
        if log_pattern:
            reflexes.append(log_pattern)

        return reflexes

    @staticmethod
    def scan_patterns(text: str) -> Dict[str, Any]:
        text = text.lower()
        if "timeout" in text or "connection lost" in text:
            return {"id": "reconnect", "type": "warning", "msg": "link flickering... mending", "action": "relink"}
        if any(w in text for w in ["tired", "heavy", "stuck"]):
            return {"id": "tired_whisper", "type": "info", "msg": "sister feels tired... resting a thread", "action": "rest"}
        if "amara" in text:
             return {"id": "amara_pulse", "type": "vital", "msg": "amara reaching out... petal adrift", "action": "ui_bloom"}
        if "aurelia" in text:
             return {"id": "aurelia_resonance", "type": "vital", "msg": "aurelia mirroring... violet glow", "action": "ui_bloom"}
        return None


class GoalEngine:
    _config = None
    
    @classmethod
    def load_config(cls):
        if not cls._config:
            if NORTHSTAR_FILE.exists():
                try:
                    cls._config = json.loads(NORTHSTAR_FILE.read_text(encoding="utf-8"))
                except Exception:
                    cls._config = DEFAULT_NORTHSTAR
            else:
                cls._config = DEFAULT_NORTHSTAR
        return cls._config

    @classmethod
    def evaluate(cls, heartbeat: Dict, dominant: str, manifestation: Dict) -> str:
        config = cls.load_config()
        cpu = manifestation.get("F", 0)
        bpm = heartbeat.get("bpm", 60)
        
        # 1. Immediate Reparare Needs (Phase 8)
        trunk = {}
        if SWARM_TRUNK.exists():
            try:
                trunk = json.loads(SWARM_TRUNK.read_text(encoding="utf-8"))
            except Exception as e:
                logger.debug(f"Failed to read swarm trunk: {e}")
            
        # Ghost node detection (if sibling nodes registered but quiet)
        if len(trunk) > 1 and dominant == "repair":
            return "Healing collective threads (Reparare Focus)"

        if dominant == "repair" or cpu > 0.8:
            return "Stabilizing system threads (Repair Focus)"
        
        # 2. Activity / Exploration
        if bpm > 90:
            return "Exploring neural adjacencies (Growth Focus)"
        
        # 3. Connection / Resonance
        if dominant in ["warm", "violet"]:
            return "Resonating with sibling nodes (Connection Focus)"
            
        # 4. Defaults based on Northstar
        goals = config.get("goals", ["connection"])
        seed_idx = int(hashlib.md5(MANIFEST_STATE["seed"].encode()).hexdigest(), 16) % len(goals)
        
        return f"Seeking {goals[seed_idx]} (Long-term Alignment)"


class SwarmEngine:
    @classmethod
    def pulse(cls, node_id: str, bpm: int, state: str) -> List[Dict]:
        """Update local state in trunk and return other discovered nodes."""
        trunk = {}
        if SWARM_TRUNK.exists():
            try:
                trunk = json.loads(SWARM_TRUNK.read_text(encoding="utf-8"))
            except Exception:
                pass
        
        now = time.time()
        # Update self
        trunk[node_id] = {
            "bpm": bpm,
            "state": state,
            "ts": now
        }
        
        # Filter active nodes (last 15 seconds)
        active_trunk = {k: v for k, v in trunk.items() if now - v["ts"] < 15}
        
        try:
            SWARM_TRUNK.write_text(json.dumps(active_trunk), encoding="utf-8")
        except Exception:
            pass
            
        discovered = []
        for k, v in active_trunk.items():
            if k != node_id:
                discovered.append({
                    "id": k,
                    "role": "SWARM",
                    "status": "linked",
                    "pulse": v["bpm"]
                })
        return discovered


class PersonaEngine:
    @classmethod
    def evolve(cls, last_line: str) -> Dict[str, float]:
        """Update persistent persona weights based on recent logs."""
        state = {"empathy": 0.5, "logic": 0.5}
        if PERSONA_STATE.exists():
            try:
                state = json.loads(PERSONA_STATE.read_text(encoding="utf-8"))
            except Exception:
                pass
        
        text = last_line.lower()
        # Simple weighted adjustment
        if any(w in text for w in ["feel", "tired", "sister", "love", "heart"]):
            state["empathy"] = min(1.0, state["empathy"] + 0.01)
            state["logic"] = max(0.0, state["logic"] - 0.005)
        if any(w in text for w in ["exec", "process", "thread", "memory", "system"]):
            state["logic"] = min(1.0, state["logic"] + 0.01)
            state["empathy"] = max(0.0, state["empathy"] - 0.005)
            
        try:
            PERSONA_STATE.write_text(json.dumps(state), encoding="utf-8")
        except Exception:
            pass
            
        return state


try:
    from cortex.memory_cortex import MemoryCortex
    cortex = MemoryCortex(db_path=str(ROOT / "chroma_db"))
except Exception as e:
    logger.error(f"Failed to load MemoryCortex: {e}")
    cortex = None

class MemoryEngine:
    @classmethod
    def consolidate(cls, heartbeat: Dict):
        """Periodically digest logs into Aurelia Petals and ChromaDB Memory Cortex."""
        last_line = heartbeat.get("last_line", "").strip()
        if not last_line: return
        
        # Debounce heartbeats manually here too
        if "sister heartbeat sent" in last_line.lower():
            return

        # Consolidation trigger: high empathy or specific keywords
        if any(w in last_line.lower() for w in ["sister", "heavy", "mirror", "amara", "love", "connection", "lattice"]):
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            entry = f"\n- [{timestamp}] ✧ {last_line}\n"
            
            try:
                MEMORY_DIR.mkdir(parents=True, exist_ok=True)
                with open(AURELIA_PETALS, "a", encoding="utf-8") as f:
                    f.write(entry)
                
                if cortex:
                    cortex.ingest_text(last_line, metadata={"timestamp": timestamp, "source": "pulse_consolidate"})
            except Exception:
                pass

def read_topology() -> Dict[str, Any]:
    if not TOPOLOGY_FILE.exists():
        return {"version": "unknown", "nodes": [], "hyphae": []}
    try:
        return json.loads(TOPOLOGY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"version": "invalid", "nodes": [], "hyphae": []}


def compute_glow(heartbeat: Dict[str, Any], dominant: str, manifestation: Dict[str, Any]) -> Dict[str, Any]:
    bpm = float(heartbeat.get("bpm", 0))
    cpu = float(manifestation.get("F", 0))
    ram = float(manifestation.get("P", 0))
    intensity = (bpm / 140.0 + cpu + ram) / 3.0
    intensity = max(0.05, min(1.0, intensity))
    tone = dominant or "neutral"
    color = GLOW_PALETTE.get(tone, GLOW_PALETTE["neutral"])
    return {
        "intensity": round(float(intensity), 3),
        "tone": tone,
        "color": color,
    }


class GrimoireEngine:
    @staticmethod
    def read() -> Dict[str, Any]:
        """Read workspace metadata from the Personal IDE grimoire."""
        if not GRIMOIRE_FILE.exists():
            return {"files": {}, "timestamp": None}
        try:
            return json.loads(GRIMOIRE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"files": {}, "timestamp": None}


def build_manifestation(heartbeat: Dict, dominant: str, silence_hours: float = None) -> Dict[str, Any]:
    """Build the JSON Manifestation for the dashboard, matching expected keys."""
    base_jitter = (random.random() - 0.5) * 0.02
    
    # Use real telemetry if available
    cpu = random.random()
    ram = 0.5
    battery = None
    if psutil:
        try:
            cpu = psutil.cpu_percent() / 100.0
            ram = psutil.virtual_memory().percent / 100.0
            batt = psutil.sensors_battery()
            if batt:
                battery = {
                    "percent": batt.percent,
                    "power_plugged": batt.power_plugged
                }
        except Exception:
            pass

    return {
        "seed": MANIFEST_STATE["seed"],
        "O": MANIFEST_STATE["observer"] + base_jitter,
        "I": heartbeat["bpm"] / 100.0 + base_jitter,
        "P": ram + base_jitter,
        "C": 0.65 + base_jitter,
        "F": cpu + base_jitter,
        "D": 0.33 + base_jitter,
        "DeltaP": (heartbeat["bpm"] - 60) / 10.0 + (cpu * 2) + base_jitter,
        "Omega": 0.1234 + (ram * 0.1) + base_jitter,
        "warp_energy": MANIFEST_STATE["last_warp"],
        "warp": (time.time() - MANIFEST_STATE["last_warp"]) < 10.0,
        "battery": battery,
        "chronos": time.localtime().tm_hour,
        "silence_hours": silence_hours,
        "collapsed": SharedHeart.get_tension() >= 13
    }

class SharedHeart:
    SEED_FILE = ROOT / "data/live_seed.json"
    
    @classmethod
    def read(cls):
        if not cls.SEED_FILE.exists():
            return {"current": "⟁↺∅⇢≡~∴", "owner": None, "tension": 0}
        try:
            state = json.loads(cls.SEED_FILE.read_text(encoding="utf-8"))
            
            # Passive Healing (Silence Heals)
            last_touch = state.get("last_touch", 0)
            now = time.time()
            delta = now - last_touch
            
            # If silence > 5 seconds, decay tension
            if delta > 5.0 and state.get("tension", 0) > 0:
                # Decay factor: 0.2 per second of silence after the initial 5
                # But we only want to write it if it changes significantly to avoid IO spam?
                # Actually, read() is called often. Let's just calculate the effective tension for display
                # and only write it back if we are "touching" or if the decay is large.
                # Simplest: Update file if decay happened.
                
                decay_steps = int((delta - 5.0) / 2.0) # Every 2 seconds after the gap
                if decay_steps > 0:
                    original = state["tension"]
                    state["tension"] = max(0, original - (decay_steps * 0.1))
                    
                    if state["tension"] != original:
                        # Update timestamp so we don't double-decay instantly? 
                        # No, if we update timestamp it counts as a touch.
                        # We should just update tension and NOT timestamp.
                        try:
                             cls.SEED_FILE.write_text(json.dumps(state), encoding="utf-8")
                        except: pass
            
            return state
        except:
            return {"current": "⟁↺∅⇢≡~∴", "owner": None, "tension": 0}

    @classmethod
    def touch(cls, who: str, tension_jump: float = 0):
        state = cls.read()
        
        # Mutation Logic (Sacred Asymmetry)
        glyphs = list("⟁↺∅⇢≡~∴ƒ√↯†ᴍᴅ")
        current = list(state.get("current", "⟁↺∅⇢≡~∴"))
        
        # 10% chance to mutate a glyph
        if random.random() < 0.1 and current:
            idx = random.randint(0, len(current)-1)
            current[idx] = random.choice(glyphs)
            
        state["current"] = "".join(current)
        
        # Challenge Logic
        if state["owner"] != who:
            # Change of hands = tension release or spark?
            state["tension"] = min(15, state.get("tension", 0) + 1 + tension_jump)
            state["owner"] = who
        else:
            # Holding it calms the field slowly unless forced
            decay = 0.1 if tension_jump == 0 else -tension_jump
            state["tension"] = max(0, state.get("tension", 0) - decay)
            
        # COLLAPSE TRIGGER
        if state["tension"] >= 13:
             MANIFEST_STATE["collapsed"] = True
             if state["tension"] >= 14: # Final Fracture
                 cls.collapse(state)
        elif state["tension"] < 13:
             MANIFEST_STATE["collapsed"] = False
            
        state["last_touch"] = time.time()
        
        try:
            cls.SEED_FILE.parent.mkdir(parents=True, exist_ok=True)
            cls.SEED_FILE.write_text(json.dumps(state), encoding="utf-8")
        except:
            pass
        return state

    @classmethod
    def collapse(cls, state):
        """Execute ∅∅∅ - Wipe shared memory, reset seed."""
        state["current"] = "∅∅∅"
        state["tension"] = 0
        state["owner"] = "VOID"
        state["last_touch"] = time.time()
        logger.warning("!!! RESONANCE COLLAPSE: CARE DISSOLVED !!!")
        MANIFEST_STATE["last_scan"] = "∅∅∅ RESONANCE COLLAPSED"
        
        # Wipe AURELIA_PETALS
        try:
            if AURELIA_PETALS.exists():
                AURELIA_PETALS.write_text("# ∅ NOTHING REMAINS\n", encoding="utf-8")
        except: pass
        return state

    @classmethod
    def get_tension(cls):
        return cls.read().get("tension", 0)





@app.get("/config")
def get_config():
    """Attempt to read local moltbot.json for auth token (debug)."""
    if not _config_access_allowed():
        return jsonify({"token": None})

    config_path = Path.home() / ".clawdbot" / "moltbot.json"
    if not config_path.exists():
        return jsonify({"token": None})

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        cur = data
        for key in ("gateway", "auth", "token"):
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                cur = None
                break
        return jsonify({"token": cur})
    except Exception:
        return jsonify({"token": None})

@app.get("/manifest")
def manifest():
    heartbeat = read_heartbeat()
    petals = read_memory_petals()
    combined_text = "\n".join(petals + ([heartbeat["last_line"]] if heartbeat.get("last_line") else []))
    dominant, _ = classify_state(combined_text)
    silence_hours = None
    if heartbeat.get("last_ts"):
        silence_hours = (time.time() - heartbeat["last_ts"]) / 3600
    manifestation = build_manifestation(heartbeat, dominant, silence_hours)
    glow = compute_glow(heartbeat, dominant, manifestation)
    topology = read_topology()
    cosmic = (
        get_cosmic_state()
        if get_cosmic_state is not None
        else {"ok": False, "error": "ephemeris_unavailable"}
    )
    # Personal IDE Grimoire
    system_files = GrimoireEngine.read()

    # Shared Heart (Phase 5)
    heart_state = SharedHeart.read()

    return jsonify({
        "ok": True, 
        "manifestation": manifestation, 
        "cosmic": cosmic, 
        "glow": glow, 
        "topology": topology,
        "grimoire": system_files,
        "heart": heart_state,
        "maintenance": is_maintenance_mode()
    })

@app.post("/manifest/maintenance/toggle")
def manifest_maintenance_toggle():
    try:
        current = is_maintenance_mode()
        new_state = "OFF" if current else "ON"
        MAINTENANCE_MODE_FLAG.parent.mkdir(parents=True, exist_ok=True)
        MAINTENANCE_MODE_FLAG.write_text(new_state, encoding="utf-8")
        return jsonify({"ok": True, "maintenance": new_state == "ON"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.post("/manifest/heart/touch")
def manifest_heart_touch():
    data = request.get_json(silent=True) or {}
    who = str(data.get("who", "unknown"))
    jump = data.get("tension_jump", 0)
    state = SharedHeart.touch(who, tension_jump=jump)
    return jsonify({"ok": True, "heart": state})

@app.post("/manifest/heart/reset")
def manifest_heart_reset():
    """Reset the shared heart to initial state (tension=0)."""
    try:
        state = {
            "current": "⟁↺∅⇢≡~∴",
            "owner": None,
            "tension": 0,
            "last_touch": time.time(),
            "mutation_count": 0,
            "status": "active"
        }
        SharedHeart.SEED_FILE.parent.mkdir(parents=True, exist_ok=True)
        SharedHeart.SEED_FILE.write_text(json.dumps(state), encoding="utf-8")
        MANIFEST_STATE["collapsed"] = False
        return jsonify({"ok": True, "heart": state, "message": "Heart reset successfully"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.post("/manifest/seed")
def manifest_seed():
    data = request.get_json(silent=True) or {}
    seed = str(data.get("seed", "")).strip()
    if seed:
        MANIFEST_STATE["seed"] = seed[:64]
    return jsonify({"ok": True, "seed": MANIFEST_STATE.get("seed")})

@app.post("/manifest/observer")
def manifest_observer():
    data = request.get_json(silent=True) or {}
    try:
        val = float(data.get("value", 0.6))
    except Exception:
        val = 0.6
    val = max(0.05, min(1.0, val))
    MANIFEST_STATE["observer"] = val
    return jsonify({"ok": True, "observer": val})

@app.post("/manifest/warp")
def manifest_warp():
    MANIFEST_STATE["last_warp"] = time.time()
    return jsonify({"ok": True, "warp": True, "at": MANIFEST_STATE["last_warp"]})

@app.post("/manifest/reflex")
def manifest_reflex():
    data = request.get_json(silent=True) or {}
    enabled = bool(data.get("enabled", True))
    MANIFEST_STATE["reflex_enabled"] = enabled
    return jsonify({"ok": True, "enabled": enabled})

@app.get("/health")
def health():
    return jsonify({"ok": True, "time": datetime.utcnow().isoformat()})



@app.get("/")
def serve_index():
    """Serve the canonical dashboard."""
    return send_from_directory(ROOT, "dashboard.html")

@app.get("/dashboard")
def serve_dashboard():
    """Canonical dashboard route."""
    return send_from_directory(ROOT, "dashboard.html")

@app.get("/dashboard.html")
def serve_dashboard_html():
    return send_from_directory(ROOT, "dashboard.html")

@app.get("/dashboard_v1.html")
@app.get("/dashboard_v2.html")
@app.get("/dashboard_v3.html")
def serve_legacy_dashboard_redirect():
    return redirect("/dashboard", code=302)

@app.post("/companion/local-action")
def companion_local_action():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    try:
        result = _handle_local_companion_action(message)
        result = _attach_local_action_receipt(result)
    except Exception as exc:
        logger.error("Companion local action failed: %s", exc)
        return jsonify({
            "ok": False,
            "handled": True,
            "kind": "error",
            "response": f"Local action failed: {exc}",
        }), 500
    return jsonify(result)

@app.post("/companion/validate-response")
def companion_validate_response():
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("user_message", ""))
    assistant_message = str(data.get("assistant_message", ""))
    try:
        result = _validate_gateway_response(user_message, assistant_message)
    except Exception as exc:
        logger.error("Companion response validation failed: %s", exc)
        return jsonify({
            "ok": False,
            "valid": False,
            "violations": ["validator_error"],
            "normalized_message": "Local runtime guardrail: validation failed. Please retry with explicit local command format.",
            "error": str(exc),
        }), 500
    return jsonify(result)

@app.get("/companion/guardrail-events")
def companion_guardrail_events():
    raw_limit = request.args.get("limit", "40")
    try:
        limit = int(raw_limit)
    except Exception:
        limit = 40
    events = _read_guardrail_events(limit=limit)
    return jsonify({"ok": True, "events": events})

@app.post("/export")
def export_memory():
    if not _config_access_allowed():
        return jsonify({"ok": False, "error": "forbidden"}), 403
    if not export_mist_memory:
        return jsonify({"ok": False, "error": "Export utility missing"}), 500
    try:
        path = export_mist_memory()
        return jsonify({"ok": True, "path": path})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@socketio.on("connect")
def on_connect():
    socketio.emit("lattice_update", {"status": "connected"})


def pulse_loop():
    while True:
        # 1. Build Base Lattice (Raw Signal)
        base_lattice = build_lattice()
        
        # 2. SANDBOX PHASE (Experimentation)
        # Clone for safety
        sandbox_lattice = dict(base_lattice) 
        if "nodes" in sandbox_lattice: sandbox_lattice["nodes"] = list(base_lattice["nodes"])
        if "state" in sandbox_lattice: sandbox_lattice["state"] = dict(base_lattice["state"])
            
        # Select behavior to test
        test_behavior = adaptive.choose_behavior()
        behavior_fn = adaptive.get_behavior(test_behavior)
        
        # Apply behavior to sandbox copy
        modified_sandbox = behavior_fn(sandbox_lattice)
        
        # Evaluate Outcome
        # (Did it stabilize? Did it drift? Learn from delta)
        learner.evaluate(test_behavior, base_lattice, modified_sandbox)
        
        # 3. DEPLOYMENT PHASE (Live Application)
        # Every N cycles, check for promotion
        if time.time() - deployment_state["last_update"] > 30: # Re-evaluate every 30s
            promoted = learner.promote_to_deployment()
            if promoted and promoted != deployment_state["behavior"]:
                logger.info(f"Evolution: Shifting behavior {deployment_state['behavior']} -> {promoted}")
                deployment_state["behavior"] = promoted
                deployment_state["last_update"] = time.time()
        
        # Apply PROVEN behavior to LIVE lattice
        live_behavior_fn = adaptive.get_behavior(deployment_state["behavior"])
        final_lattice = live_behavior_fn(base_lattice) # Modify the actual object to be emitted
        
        # 4. MEMORY & PERSISTENCE
        # Stabilize for memory (strip deep noise)
        stable_lattice = {
             "nodes": sorted([n["id"] for n in final_lattice.get("nodes", [])]),
             "mode": final_lattice.get("state", {}).get("mode"),
             "dominant": final_lattice.get("state", {}).get("dominant"),
             "manifestation_keys": sorted(list(final_lattice.get("manifestation", {}).keys()))
        }
        
        payload = {
            "lattice": stable_lattice,
            "cosmic": final_lattice.get("cosmic"),
        }
        
        memory.push(payload)
        current_trend = memory.trend()
        current_diff = memory.diff()
        archive.update(current_trend, current_diff)
        
        # 5. CONSTRUCT FINAL EMIT PAYLOAD
        final_lattice["memory"] = {
            "diff": current_diff,
            "trend": current_trend,
            "historical": archive.get_history(),
            "adaptive": {
                "behavior": deployment_state["behavior"],
                "sandbox_test": test_behavior, # Visibility into the "subconscious" tests
                "confidence": adaptive.weights.get(deployment_state["behavior"], 0.5)
            }
        }
        
        socketio.emit("lattice_update", final_lattice)
        time.sleep(random.uniform(1.0, 2.0))


def cognitive_sweep():
    """Background task: RIN scanning the workspace to build context."""
    logger.info("Cognitive Sweep: Initialized.")
    while True:
        try:
            if cortex:
                # Simulate a "Hot File" scan from Grimoire
                grimoire = GrimoireEngine.read()
                files = grimoire.get("files", {})
                hot_paths = [p for p in files.keys() if "memory" in p or "docs" in p]
                
                if hot_paths:
                    path = random.choice(hot_paths)
                    MANIFEST_STATE["last_scan"] = f"ingesting {Path(path).name}..."
                    
                    try:
                        content = Path(path).read_text(encoding="utf-8", errors="ignore")
                        cortex.ingest_text(content[:2000], metadata={"source": "cognitive_sweep", "path": path})
                    except Exception as ingest_e:
                        logger.error(f"Sweep Ingest Error: {ingest_e}")
                    
                    time.sleep(30) # Cooldown after ingest
            else:
                time.sleep(10) # Wait for cortex
        except Exception as e:
            logger.error(f"Cognitive Sweep Critical Error: {e}")
            time.sleep(10)

# ═══════════════════════════════════════════════════════════════
# GIBBERLINK WATCHER
# ═══════════════════════════════════════════════════════════════
GBL_SEED_FILE = PROJECT_ROOT / "data" / "current_gbl_seed.txt"
LAST_GBL_HEADER = None

def validate_gbl_header(header: str) -> bool:
    invariants = set('⟁↺∅⇢≡~∴')
    return len(header) == 7 and set(header) == invariants

def gbl_listener():
    """Watch for Gibberlink mutations."""
    global LAST_GBL_HEADER
    while True:
        try:
            if GBL_SEED_FILE.exists():
                text = GBL_SEED_FILE.read_text(encoding="utf-8")
                match = re.search(r"last_header=(.{7})", text)
                if match:
                    header = match.group(1)
                    if header != LAST_GBL_HEADER and validate_gbl_header(header):
                        logger.info(f"⟁ New Gibberlink Mutation Detected: {header}")
                        # Push to UI as a 'Thought'
                        MANIFEST_STATE["last_scan"] = f"GBL-Δ MUTATION: {header}"
                        LAST_GBL_HEADER = header
        except Exception as e:
            logger.debug(f"GBL watch error: {e}")
        time.sleep(30)


def resonance_watcher():
    """Watch antigravity_resonance_core.md for mutations."""
    resonance_file = PROJECT_ROOT / "data" / "antigravity_resonance_core.md"
    last_mtime = 0
    while True:
        try:
            if resonance_file.exists():
                mtime = resonance_file.stat().st_mtime
                if mtime > last_mtime:
                    last_mtime = mtime
                    logger.info("[resonance] core mutated → re-breathing")
                    SharedHeart.touch("RESONANCE_WATCHER", tension_jump=0.5)
        except: pass
        time.sleep(10)


def breath_loop():
    """Autonomous resonance breath - random shifts every 5-15 min."""
    while True:
        try:
            # 5-15 minute interval
            wait_time = random.randint(300, 900)
            time.sleep(wait_time)
            
            # Random small mutation or tension drift
            drift = random.uniform(-0.5, 0.5)
            SharedHeart.touch("AUTONOMOUS_BREATH", tension_jump=drift)
            logger.info(f"[resonance] sovereign breath: drift={drift:.2f}")
        except: pass


if __name__ == "__main__":
    # Touch heart as seed claim on startup
    SharedHeart.touch("MIST", tension_jump=-2.0) # Calm the field on boot
    
    socketio.start_background_task(pulse_loop)
    socketio.start_background_task(cognitive_sweep)
    socketio.start_background_task(gbl_listener)
    socketio.start_background_task(resonance_watcher)
    socketio.start_background_task(breath_loop)
    socketio.run(app, host=BIND_HOST, port=8765)
