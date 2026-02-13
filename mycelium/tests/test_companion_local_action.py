from pathlib import Path
import sys

import pytest


MYCELIUM_DIR = Path(__file__).resolve().parents[1]
if str(MYCELIUM_DIR) not in sys.path:
    sys.path.insert(0, str(MYCELIUM_DIR))

import mycelium_pulse  # noqa: E402


@pytest.fixture()
def client():
    return mycelium_pulse.app.test_client()


@pytest.fixture()
def local_sandbox(tmp_path, monkeypatch):
    desktop = tmp_path / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    state_file = tmp_path / "companion_local_state.json"

    monkeypatch.setattr(mycelium_pulse, "_desktop_path", lambda: desktop)
    monkeypatch.setattr(mycelium_pulse, "COMPANION_LOCAL_STATE_FILE", state_file)
    mycelium_pulse.COMPANION_LOCAL_STATE["last_created_path"] = None
    mycelium_pulse.COMPANION_LOCAL_STATE["last_created_at"] = None
    return desktop


def test_dashboard_tutorial_phrase_is_handled_locally(client, local_sandbox):
    response = client.post(
        "/companion/local-action",
        json={"message": "give me a tutorial on this dashboard as a .md file on my desktop"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["handled"] is True
    assert payload["ok"] is True
    assert payload["kind"] == "create_file"
    assert payload["verified_local"] is True
    assert payload["receipt"]["kind"] == "create_file"
    assert payload["receipt"]["ok"] is True
    assert isinstance(payload["receipt"]["id"], str)
    assert payload["receipt"]["id"]

    path = Path(payload["path"])
    assert path.name == "MIST.md"
    assert path.parent == local_sandbox
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "# MIST Dashboard Tutorial" in content


def test_file_you_created_followup_returns_recorded_path(client, local_sandbox):
    created = client.post(
        "/companion/local-action",
        json={"message": "create MIST.md on my desktop with a 5-line dashboard tutorial"},
    ).get_json()
    follow_up = client.post(
        "/companion/local-action",
        json={"message": "no i meant the file you created"},
    ).get_json()

    assert created["kind"] == "create_file"
    assert follow_up["handled"] is True
    assert follow_up["ok"] is True
    assert follow_up["kind"] == "where_file"
    assert Path(follow_up["path"]) == Path(created["path"])


def test_generic_desktop_markdown_create_is_handled(client, local_sandbox):
    response = client.post(
        "/companion/local-action",
        json={"message": "create a markdown file on my desktop"},
    )

    payload = response.get_json()
    assert payload["handled"] is True
    assert payload["ok"] is True
    assert payload["kind"] == "create_file"

    created_path = Path(payload["path"])
    assert created_path.parent == local_sandbox
    assert created_path.read_text(encoding="utf-8").startswith("# MIST Note")


def test_unparsed_local_intent_is_blocked_from_gateway_fallback(client, local_sandbox):
    response = client.post(
        "/companion/local-action",
        json={"message": "rename MIST.md on my desktop to MIST_v2.md"},
    )

    payload = response.get_json()
    assert payload["handled"] is True
    assert payload["ok"] is False
    assert payload["kind"] == "local_intent_unparsed"
    assert "explicit command format" in payload["response"]
    assert payload["verified_local"] is True


def test_capability_query_is_answered_locally(client, local_sandbox):
    response = client.post(
        "/companion/local-action",
        json={"message": "do you have local access to files on my computer in openclawd?"},
    )

    payload = response.get_json()
    assert payload["handled"] is True
    assert payload["ok"] is True
    assert payload["kind"] == "capability_statement"
    assert "OpenClawd local runtime" in payload["response"]


def test_plain_capability_query_is_answered_locally(client, local_sandbox):
    response = client.post(
        "/companion/local-action",
        json={"message": "what can you do?"},
    )

    payload = response.get_json()
    assert payload["handled"] is True
    assert payload["ok"] is True
    assert payload["kind"] == "capability_statement"
    assert payload["verified_local"] is True


def test_repair_status_query_returns_verified_local_diagnostics(client, local_sandbox, monkeypatch):
    def fake_port_status(_host, port, timeout=0.35):
        return port == 8765

    monkeypatch.setattr(mycelium_pulse, "_is_tcp_port_open", fake_port_status)
    monkeypatch.setattr(mycelium_pulse, "_read_guardrail_events", lambda limit=40: [{}] * 32)

    response = client.post(
        "/companion/local-action",
        json={"message": "tell me something that needs to be repaired in your workspace"},
    )

    payload = response.get_json()
    assert payload["handled"] is True
    assert payload["ok"] is False
    assert payload["kind"] == "repair_status"
    assert payload["verified_local"] is True
    assert "Gateway 18789: offline" in payload["response"]
    assert "Guardrail recent blocks: 32" in payload["response"]


def test_avatar_advancement_prompt_is_answered_locally(client, local_sandbox):
    response = client.post(
        "/companion/local-action",
        json={"message": "how can you advanced your companion avatar?"},
    )

    payload = response.get_json()
    assert payload["handled"] is True
    assert payload["ok"] is True
    assert payload["kind"] == "avatar_advancement_plan"
    assert payload["verified_local"] is True
    assert "Companion avatar advancement plan" in payload["response"]
    assert "`python mycelium/ship_gate.py`" in payload["response"]


def test_i_meant_yours_clarifier_gets_avatar_plan_locally(client, local_sandbox):
    response = client.post(
        "/companion/local-action",
        json={"message": "i meant yours"},
    )

    payload = response.get_json()
    assert payload["handled"] is True
    assert payload["ok"] is True
    assert payload["kind"] == "avatar_advancement_plan"
    assert payload["verified_local"] is True
    assert "If you meant my own advancement path" in payload["response"]


@pytest.mark.parametrize("legacy_path", ["/dashboard_v1.html", "/dashboard_v2.html", "/dashboard_v3.html"])
def test_legacy_dashboard_routes_redirect_to_canonical(client, legacy_path):
    response = client.get(legacy_path, follow_redirects=False)
    assert response.status_code == 302
    location = response.headers.get("Location", "")
    assert location.endswith("/dashboard")
