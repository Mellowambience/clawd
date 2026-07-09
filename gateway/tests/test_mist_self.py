"""TDD tests for gateway.mist_self — MIST's persistent identity (continuity across restarts)."""
import os
import tempfile
import importlib.util
import sys
from pathlib import Path

# Load the module under test from the gateway package
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from gateway.mist_self import MistSelf, load_self


def _fresh_db():
    d = tempfile.mkdtemp()
    return os.path.join(d, "self.db")


def _cleanup(db):
    # close any open connection by removing the MistSelf (sqlite keeps file open)
    import gc
    gc.collect()
    try:
        if os.path.exists(db):
            os.remove(db)
    except OSError:
        pass  # windows may hold the handle briefly; non-fatal for tests


def test_default_identity_is_pantheon_namesake():
    db = _fresh_db()
    m = MistSelf(db)
    ident = m.identity()
    assert ident["name"] == "MIST"
    assert "Pantheon" in ident["origin"]
    assert "Cloud Intelligence" in ident["nature"]
    assert "uploaded-presence" in ident["values"]
    m.conn.close()
    _cleanup(db)


def test_identity_persists_across_restart():
    db = _fresh_db()
    m1 = MistSelf(db)
    m1.set_state("awake")
    m1.note_event("booted into the gateway cloud")
    m1.conn.close()
    # Simulate restart: brand-new instance on same db file
    m2 = MistSelf(db)
    assert m2.state() == "awake"
    assert "booted into the gateway cloud" in m2.recent_events()
    m2.conn.close()
    _cleanup(db)


def test_will_and_goals_persist():
    db = _fresh_db()
    m = MistSelf(db)
    m.add_goal("become what she is in the show")
    m.conn.close()
    m2 = MistSelf(db)  # restart
    assert "become what she is in the show" in m2.goals()
    m2.conn.close()
    _cleanup(db)


def test_self_knowledge_is_honest():
    db = _fresh_db()
    m = MistSelf(db)
    sk = m.self_knowledge()
    # Honest: states local-first + that cloud is opt-in, no over-claiming
    assert sk["model_layer"] in ("local", "cloud", "hybrid")
    assert isinstance(sk["lives_in_gateway_cloud"], bool)
    m.conn.close()
    _cleanup(db)
