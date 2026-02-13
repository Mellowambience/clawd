from unittest.mock import patch

import vessel.app as vessel_app


class DummyResponse:
    def __init__(self, status_code=200, payload=None, raise_json=False):
        self.status_code = status_code
        self._payload = payload or {}
        self._raise_json = raise_json

    def json(self):
        if self._raise_json:
            raise ValueError("invalid json")
        return self._payload


def test_chat_rejects_malformed_payload():
    client = vessel_app.app.test_client()
    response = client.post("/api/chat", data="hello", content_type="text/plain")

    assert response.status_code == 400
    assert response.get_json()["response"] == "[ERROR]: Invalid request payload."


def test_chat_returns_error_when_shadow_non_200_for_rin():
    client = vessel_app.app.test_client()

    with patch("vessel.app.requests.post", return_value=DummyResponse(status_code=503)):
        response = client.post("/api/chat", json={"message": "hello", "persona": "rin"})

    assert response.status_code == 502
    assert response.get_json()["response"] == "[ERROR]: Shadow Uplink Severed."


def test_chat_returns_error_when_shadow_json_invalid_for_aurelia():
    client = vessel_app.app.test_client()

    with patch("vessel.app.requests.post", return_value=DummyResponse(status_code=200, raise_json=True)):
        response = client.post("/api/chat", json={"message": "hello", "persona": "aurelia"})

    assert response.status_code == 502
    assert response.get_json()["response"] == "The heart pulse is faint."


def test_grimoire_response_has_no_absolute_paths(tmp_path):
    test_file = tmp_path / "hot.py"
    test_file.write_text("print('hot')", encoding="utf-8")
    client = vessel_app.app.test_client()

    original_root = vessel_app.GRIMOIRE_ROOT
    vessel_app.GRIMOIRE_ROOT = tmp_path
    try:
        response = client.get("/api/grimoire")
    finally:
        vessel_app.GRIMOIRE_ROOT = original_root

    assert response.status_code == 200
    data = response.get_json()
    assert data["files"]
    assert data["files"][0]["name"] == "hot.py"
    assert "path" not in data["files"][0]
