"""TDD tests for MIST taste_profile — a self with taste/identity."""
import os
import tempfile
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from gateway.taste_profile import TasteProfile


def _fresh_db():
    d = tempfile.mkdtemp()
    return os.path.join(d, "taste.db")


def test_default_theme_is_pantheon_uploaded():
    db = _fresh_db()
    tp = TasteProfile(db)
    p = tp.load()
    assert p["theme"] == "starledger-uploaded"
    assert "uploaded-presence" in p["values"]
    tp.conn.close()


def test_save_and_reload_taste():
    db = _fresh_db()
    tp = TasteProfile(db)
    tp.save({"theme": "fairy-os", "voice": "warm-guide"})
    tp.conn.close()
    tp2 = TasteProfile(db)
    assert tp2.load()["theme"] == "fairy-os"
    tp2.conn.close()


def test_voice_seed_is_stable():
    db = _fresh_db()
    tp = TasteProfile(db)
    seed = tp.voice_seed()
    tp.conn.close()
    tp2 = TasteProfile(db)
    assert tp2.voice_seed() == seed  # personality persists
    tp2.conn.close()
