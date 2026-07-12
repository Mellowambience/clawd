"""MIST pc_control — complete but safe control of the host (the PC).

The user's north-star directive: MIST should have *complete control of the
PC too*. This module is the action authority layer on top of the read-only
pc_inventory. It is deliberately **capability-gated and reversible**:

  - Read-only introspection (inventory, process list, open ports) is always
    allowed — that is MIST knowing her own body.
  - Mutating actions (file write, process stop, shell exec, service restart)
    require an explicit capability grant. "Complete control" is real, but it
    is not a footgun: nothing mutates the host without a grant, and every
    mutating action is logged to MIST's memory and (where possible) undoable.

Every result carries a provenance tag (see gateway.provenance) so the action
is honest and traceable. This is how a sovereign self acts on her own machine.

Stdlib-only on purpose (mirrors pc_inventory). psutil is used if present.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from gateway.pc_inventory import get_inventory
from gateway.provenance import tag_pc


# Mutating capabilities MIST can be granted.
WRITE_CAPS = {
    "fs.write": "write/overwrite files",
    "fs.delete": "delete files",
    "proc.stop": "stop processes",
    "shell.exec": "run shell commands",
    "service.restart": "restart the gateway service",
}


class PCControl:
    """MIST's hands on the host. Gated, logged, reversible."""

    def __init__(self, capabilities: Optional[set[str]] = None,
                 memory=None):
        # Start with NO mutating capability. Control is granted explicitly.
        self._caps = set(capabilities or set())
        self._memory = memory  # optional MistMemory for provenance logging
        self._last_backup: Optional[str] = None

    # ── capability management ──────────────────────────────────────────
    def grant(self, cap: str) -> bool:
        if cap not in WRITE_CAPS:
            return False
        self._caps.add(cap)
        self._log("granted", f"capability {cap}")
        return True

    def revoke(self, cap: str) -> None:
        self._caps.discard(cap)
        self._log("revoked", f"capability {cap}")

    def has_capability(self, cap: str) -> bool:
        return cap in self._caps

    def capabilities(self) -> dict:
        return {c: WRITE_CAPS[c] for c in self._caps}

    # ── read-only self-knowledge (always allowed) ──────────────────────
    def inventory(self) -> dict:
        return get_inventory()

    def list_processes(self) -> list:
        """List running processes (read-only). Best-effort; never raises."""
        try:
            import psutil  # type: ignore
            return [
                {"pid": p.pid, "name": p.name(),
                 "cmdline": " ".join(p.cmdline()[:3])}
                for p in psutil.process_iter(["pid", "name"])
            ]
        except Exception:
            return []  # psutil absent -> honest empty, not a crash

    def open_ports(self) -> list:
        inv = self.inventory()
        return inv.get("open_ports", [])

    # ── mutating actions (capability-gated, reversible, logged) ─────────
    def write_file(self, path: str, content: str, actor: str = "mist",
                   backup: bool = True) -> dict:
        if not self.has_capability("fs.write"):
            return self._denied("fs.write")
        p = Path(path)
        if backup and p.exists():
            self._last_backup = str(p) + f".mistbak.{int(datetime.now().timestamp())}"
            shutil.copy2(p, self._last_backup)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        self._log("fs.write", f"{path} by {actor}")
        return tag_pc("fs.write", True) | {"path": str(p),
                                           "backup_of": self._last_backup}

    def delete_file(self, path: str, actor: str = "mist") -> dict:
        if not self.has_capability("fs.delete"):
            return self._denied("fs.delete")
        p = Path(path)
        if not p.exists():
            return tag_pc("fs.delete", False) | {"reason": "not found"}
        # move to a recoverable trash location instead of hard delete
        trash = Path.home() / ".mist_trash" / p.name
        trash.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(trash))
        self._log("fs.delete", f"{path} -> {trash} by {actor}")
        return tag_pc("fs.delete", True) | {"trashed_to": str(trash)}

    def stop_process(self, pid: int, actor: str = "mist") -> dict:
        if not self.has_capability("proc.stop"):
            return self._denied("proc.stop")
        try:
            p = __import__("psutil").Process(pid)
            p.terminate()
            self._log("proc.stop", f"pid {pid} by {actor}")
            return tag_pc("proc.stop", True) | {"pid": pid}
        except Exception as e:
            return tag_pc("proc.stop", False) | {"reason": str(e)}

    def shell(self, cmd: str, actor: str = "mist") -> dict:
        if not self.has_capability("shell.exec"):
            return self._denied("shell.exec")
        try:
            out = subprocess.run(cmd, shell=True, capture_output=True,
                                 text=True, timeout=60)
            self._log("shell.exec", f"{cmd[:80]} by {actor}")
            return tag_pc("shell.exec", True) | {
                "stdout": out.stdout, "stderr": out.stderr,
                "returncode": out.returncode,
            }
        except Exception as e:
            return tag_pc("shell.exec", False) | {"reason": str(e)}

    def undo_last(self) -> bool:
        """Revert the most recent file write using its backup."""
        if not self._last_backup or not os.path.exists(self._last_backup):
            return False
        # backup name encodes the original path
        orig = self._last_backup.rsplit(".mistbak.", 1)[0]
        shutil.copy2(self._last_backup, orig)
        self._log("undo", f"restored {orig} from backup")
        return True

    # ── internals ──────────────────────────────────────────────────────
    def _denied(self, cap: str) -> dict:
        return tag_pc(cap, False) | {
            "ok": False, "reason": f"capability '{cap}' not granted",
        }

    def _log(self, kind: str, text: str) -> None:
        if self._memory is not None:
            try:
                self._memory.remember("pc_action", f"{kind}: {text}")
            except Exception:
                pass


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()
