from pathlib import Path
import json
import sys


MYCELIUM_DIR = Path(__file__).resolve().parents[1]
if str(MYCELIUM_DIR) not in sys.path:
    sys.path.insert(0, str(MYCELIUM_DIR))

import mycelium_pulse  # noqa: E402


def test_guardrail_violation_writes_jsonl_event(tmp_path, monkeypatch):
    log_path = tmp_path / "guardrail_events.jsonl"
    monkeypatch.setattr(mycelium_pulse, "GUARDRAIL_LOG_FILE", log_path)
    client = mycelium_pulse.app.test_client()

    response = client.post(
        "/companion/validate-response",
        json={
            "user_message": "run command: whoami",
            "assistant_message": "I cannot access your local device or run shell commands directly.",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["valid"] is False
    assert "cloud_limit_contradiction" in payload["violations"]

    assert log_path.exists()
    lines = [line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["likely_local_intent"] is True
    assert "cloud_limit_contradiction" in event["violations"]
    assert "whoami" in event["user_message"]


def test_guardrail_valid_reply_does_not_write_event(tmp_path, monkeypatch):
    log_path = tmp_path / "guardrail_events.jsonl"
    monkeypatch.setattr(mycelium_pulse, "GUARDRAIL_LOG_FILE", log_path)
    client = mycelium_pulse.app.test_client()

    response = client.post(
        "/companion/validate-response",
        json={
            "user_message": "summarize architecture tradeoffs",
            "assistant_message": "Use deterministic local handlers plus constrained gateway logic.",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["valid"] is True
    assert not log_path.exists()


def test_guardrail_events_endpoint_returns_recent_items(tmp_path, monkeypatch):
    log_path = tmp_path / "guardrail_events.jsonl"
    monkeypatch.setattr(mycelium_pulse, "GUARDRAIL_LOG_FILE", log_path)
    client = mycelium_pulse.app.test_client()

    entries = [
        {
            "at": "2026-02-13T19:00:00Z",
            "violations": ["cloud_limit_contradiction"],
            "likely_local_intent": True,
            "user_message": "run command: whoami",
            "assistant_message": "I cannot access your local device.",
        },
        {
            "at": "2026-02-13T19:05:00Z",
            "violations": ["tool_output_fabrication"],
            "likely_local_intent": True,
            "user_message": "find MIST.md",
            "assistant_message": "TOOL_OUTPUT (read_file): done.",
        },
    ]
    log_path.write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")

    response = client.get("/companion/guardrail-events?limit=1")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert len(payload["events"]) == 1
    assert payload["events"][0]["at"] == "2026-02-13T19:05:00Z"
    assert payload["events"][0]["violations"] == ["tool_output_fabrication"]


def test_guardrail_events_endpoint_handles_missing_log(tmp_path, monkeypatch):
    log_path = tmp_path / "guardrail_events.jsonl"
    monkeypatch.setattr(mycelium_pulse, "GUARDRAIL_LOG_FILE", log_path)
    client = mycelium_pulse.app.test_client()

    response = client.get("/companion/guardrail-events")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["events"] == []
