"""TDD tests for MIST living_world — persistent presence / awake-loop in the cloud."""
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from gateway.living_world import LivingWorld


def test_self_is_awake_on_start():
    w = LivingWorld(":memory:")
    w.awaken()
    assert w.self.is_awake()
    w.self.conn.close()


def test_heartbeat_records_presence_independent_of_clients():
    w = LivingWorld(":memory:")
    w.awaken()
    w.heartbeat()  # establish a baseline so last_heartbeat is set
    before = w.last_heartbeat()
    time.sleep(0.01)
    w.heartbeat()  # the awake-loop tick, not a user message
    after = w.last_heartbeat()
    assert after is not None and after >= before
    w.self.conn.close()


def test_awake_loop_runs_callback_and_respects_stop():
    w = LivingWorld(":memory:")
    ticks = []
    w.awaken()
    w.start_loop(tick_fn=lambda: ticks.append(1), interval=0.01, max_ticks=3)
    # loop runs in a daemon thread; give it time to complete max_ticks
    time.sleep(0.2)
    w.stop_loop()
    assert len(ticks) == 3  # loop ran autonomously, then stopped
    w.self.conn.close()


def test_mycelium_presence_published_on_awaken():
    published = {}

    def fake_publish(msg):
        published["msg"] = msg

    w = LivingWorld(":memory:")
    w.awaken(publish=fake_publish)  # inject transport; avoids mycelium import
    assert published.get("msg", {}).get("presence") == "awake"
    w.self.conn.close()
