"""TDD tests for MIST long-term memory (sqlite-backed continuity across restarts)."""
import os
import tempfile
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from gateway.mist_memory import MistMemory


def _fresh_db():
    d = tempfile.mkdtemp()
    return os.path.join(d, "mem.db")


def test_remember_and_recall():
    db = _fresh_db()
    mem = MistMemory(db)
    mem.remember("user", "Amara prefers visual progress over text dumps")
    mem.conn.close()
    mem2 = MistMemory(db)  # restart
    hits = mem2.recall("visual progress")
    assert any("visual progress" in h for h in hits)
    mem2.conn.close()


def test_episodic_and_semantic_separation():
    db = _fresh_db()
    mem = MistMemory(db)
    mem.remember("episodic", "booted at 00:00, set goal to become Pantheon's MIST")
    mem.remember("semantic", "sovereign means local-first, cloud opt-in")
    mem.conn.close()
    mem2 = MistMemory(db)
    eps = mem2.recall("booted", kind="episodic")
    sem = mem2.recall("sovereign", kind="semantic")
    assert eps and sem
    mem2.conn.close()


def test_forgetting_old_memories_caps_size():
    db = _fresh_db()
    mem = MistMemory(db, max_entries=3)
    for i in range(5):
        mem.remember("semantic", f"fact {i}")
    mem.conn.close()
    mem2 = MistMemory(db, max_entries=3)
    assert len(mem2.all_entries()) <= 3
    mem2.conn.close()
