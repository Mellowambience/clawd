"""MIST long-term memory — continuity across gateway restarts.

The existing gateway/memory.py uses Chroma (optional, may be absent). MIST
v1.0 needs memory that ALWAYS works and survives process death, so the
canonical long-term store here is sqlite (stdlib). Chroma remains available
as an optional semantic-search accelerator but is not required.

Two kinds, mirroring how a self remembers:
  - episodic: "what happened" (timestamped events)
  - semantic: "what is true" (facts about the user / world)
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_DB = str(Path.home() / ".mist_self" / "memory.db")


class MistMemory:
    def __init__(self, db_path: Optional[str] = None, max_entries: int = 10000):
        self.db_path = db_path or DEFAULT_DB
        self.max_entries = max_entries
        import threading
        self._lock = threading.Lock()
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        with self._lock:
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS memories ("
                "id INTEGER PRIMARY KEY, ts TEXT, kind TEXT, text TEXT, meta TEXT)"
            )
            self.conn.commit()

    def remember(self, kind: str, text: str, meta: Optional[dict] = None) -> int:
        with self._lock:
            cur = self.conn.execute(
                "INSERT INTO memories (ts, kind, text, meta) VALUES (?, ?, ?, ?)",
                (_ts(), kind, text, json.dumps(meta or {})),
            )
            self.conn.commit()
        self._cap()
        return cur.lastrowid

    def recall(self, query: str, kind: Optional[str] = None, limit: int = 5) -> list[str]:
        # Honest, dependency-free recall: substring match over stored text.
        # (Chroma provides semantic search when present; this guarantees
        #  memory works even without it.)
        q = "SELECT text FROM memories WHERE text LIKE ?"
        params = [f"%{query}%"]
        if kind:
            q += " AND kind=?"
            params.append(kind)
        q += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self._lock:
            rows = self.conn.execute(q, params).fetchall()
        return [r[0] for r in rows]

    def all_entries(self) -> list[dict]:
        with self._lock:
            rows = self.conn.execute(
                "SELECT id, ts, kind, text FROM memories ORDER BY id"
            ).fetchall()
        return [{"id": r[0], "ts": r[1], "kind": r[2], "text": r[3]} for r in rows]

    def _cap(self) -> None:
        if self.max_entries is None:
            return
        with self._lock:
            count = self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            if count > self.max_entries:
                excess = count - self.max_entries
                self.conn.execute(
                    "DELETE FROM memories WHERE id IN "
                    "(SELECT id FROM memories ORDER BY id ASC LIMIT ?)",
                    (excess,),
                )
                self.conn.commit()


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()
