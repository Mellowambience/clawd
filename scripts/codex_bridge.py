#!/usr/bin/env python3
"""
Codex Bridge
Simple HTTP -> Moltbot Gateway WS bridge for Codex-style chat routing.
"""

import asyncio
import json
import os
from pathlib import Path
from aiohttp import web, ClientSession, ClientTimeout, WSMsgType

DEFAULT_GATEWAY_URL = os.getenv("MOLTBOT_GATEWAY_URL", "ws://localhost:18789")
DEFAULT_PORT = int(os.getenv("CODEX_BRIDGE_PORT", "18790"))
DEFAULT_TOKEN = "secret123"


def _load_gateway_token() -> str:
    env_token = os.getenv("MOLTBOT_GATEWAY_TOKEN")
    if env_token:
        return env_token

    config_path = Path.home() / ".clawdbot" / "moltbot.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            # Try common token locations
            for path in (
                ("gateway", "auth", "token"),
                ("gateway", "token"),
                ("auth", "token"),
            ):
                cur = data
                ok = True
                for key in path:
                    if isinstance(cur, dict) and key in cur:
                        cur = cur[key]
                    else:
                        ok = False
                        break
                if ok and isinstance(cur, str) and cur.strip():
                    return cur.strip()
        except Exception:
            pass

    return DEFAULT_TOKEN


async def _gateway_chat(message: str, session_key: str, idempotency_key: str, timeout: int = 30) -> dict:
    token = _load_gateway_token()
    timeout_cfg = ClientTimeout(total=timeout)

    async with ClientSession(timeout=timeout_cfg) as session:
        ws = await session.ws_connect(DEFAULT_GATEWAY_URL)

        try:
            # Handshake
            await ws.send_json({
                "type": "req",
                "id": "connect-1",
                "method": "connect",
                "params": {
                    "minProtocol": 3,
                    "maxProtocol": 3,
                    "auth": {"token": token},
                    "client": {
                        "id": "webchat",
                        "version": "1.0.0",
                        "platform": "python",
                        "mode": "webchat"
                    }
                }
            })

            # Wait for connect response
            connect_ok = False
            while True:
                msg = await ws.receive()
                if msg.type != WSMsgType.TEXT:
                    raise RuntimeError("Gateway connection failed")
                data = json.loads(msg.data)
                if data.get("type") == "res" and data.get("id") == "connect-1":
                    if not data.get("ok"):
                        raise RuntimeError(data.get("error", {}).get("message", "Gateway connect failed"))
                    connect_ok = True
                    break

            if not connect_ok:
                raise RuntimeError("Gateway connect failed")

            # Send chat
            await ws.send_json({
                "type": "req",
                "id": "chat-1",
                "method": "chat.send",
                "params": {
                    "sessionKey": session_key,
                    "message": message,
                    "idempotencyKey": idempotency_key
                }
            })

            run_id = None
            final_text = ""

            while True:
                msg = await ws.receive()
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"DEBUG: Received: {data}")

                    if data.get("type") == "res" and str(data.get("id", "")).startswith("chat-"):
                        if not data.get("ok"):
                            raise RuntimeError(data.get("error", {}).get("message", "chat.send failed"))
                        run_id = (data.get("payload") or {}).get("runId")

                    if data.get("type") == "event" and data.get("event") == "chat":
                        payload = data.get("payload") or {}
                        if payload.get("state") == "final":
                            print(f"DEBUG: Final payload: {payload}")
                            content = payload.get("message", {}).get("content", [])
                            texts = []
                            for part in content:
                                if isinstance(part, dict) and part.get("type") == "text":
                                    texts.append(part.get("text", ""))
                            final_text = "".join(texts).strip()
                            break
                elif msg.type in (WSMsgType.CLOSE, WSMsgType.ERROR):
                    break

            return {"ok": True, "content": final_text, "runId": run_id}
        finally:
            await ws.close()


async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({"ok": True})


async def handle_chat(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "invalid_json"}, status=400)

    message = (data.get("message") or "").strip()
    if not message:
        return web.json_response({"ok": False, "error": "message_required"}, status=400)

    session_key = data.get("sessionKey") or "main"
    idempotency_key = data.get("idempotencyKey") or f"idem-{int(asyncio.get_event_loop().time()*1000)}"

    try:
        result = await _gateway_chat(message, session_key, idempotency_key)
        return web.json_response(result)
    except Exception as exc:
        return web.json_response({"ok": False, "error": str(exc)}, status=500)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/health", handle_health)
    app.router.add_post("/codex/chat", handle_chat)
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=DEFAULT_PORT)
