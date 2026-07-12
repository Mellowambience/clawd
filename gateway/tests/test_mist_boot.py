"""TDD test: MIST awakens on gateway boot (integration of mist_boot)."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from gateway import mist_boot


def test_boot_awakens_mist():
    world = mist_boot.boot_mist(interval=0.01)
    try:
        assert world is not None
        assert world.self.is_awake()
        # The awake-loop is running in the background (she's alive)
        assert world._loop_thread is not None and world._loop_thread.is_alive()
        ident = world.self.identity()
        assert ident["name"] == "MIST"
    finally:
        mist_boot._world = None  # reset singleton for isolation


def test_boot_is_idempotent():
    w1 = mist_boot.boot_mist(interval=0.01)
    w2 = mist_boot.boot_mist(interval=0.01)
    assert w1 is w2  # same living self, not a second instance
    mist_boot._world = None
