#!/usr/bin/env python3
"""
Verifies MIST gateway WebSocket protocol (same as lib/mist-gateway-client.ts).
Usage: python scripts/verify_gateway_client.py [host] [port]
- With gateway DOWN: exits non-zero, prints "OFFLINE".
- With gateway UP: exits 0, prints "OK" and first 200 chars of reply.
"""

import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("Install websockets: pip install websockets")
    sys.exit(2)


async def send_to_gateway(host: str, port: int, message: str):
    url = f"ws://{host}:{port}"
    result = {"ok": False, "error": "unknown"}

    def next_id():
        import time
        import random
        return f"req-{int(time.time()*1000)}-{random.randint(10000, 99999)}"

    try:
        async with websockets.connect(url, open_timeout=3, close_timeout=1) as ws:
            # Connect handshake
            connect_id = next_id()
            await ws.send(json.dumps({"type": "req", "id": connect_id, "method": "connect", "params": {}}))
            res = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
            if res.get("type") != "res" or res.get("id") != connect_id or not res.get("ok"):
                result["error"] = "Handshake failed"
                return result

            # Chat
            chat_id = next_id()
            await ws.send(json.dumps({"type": "req", "id": chat_id, "method": "chat.send", "params": {"message": message}}))
            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=120)
                data = json.loads(raw)
                if data.get("type") == "event" and data.get("event") == "chat":
                    payload = data.get("payload") or {}
                    if payload.get("state") == "final":
                        content = payload.get("message") or {}
                        parts = content.get("content") or []
                        if not isinstance(parts, list):
                            parts = [parts]
                        text = "".join(p.get("text", "") for p in parts).strip()
                        result["ok"] = True
                        result["text"] = text or "(no response)"
                        return result
    except asyncio.TimeoutError:
        result["error"] = "Timeout (gateway offline or slow)."
    except Exception as e:
        result["error"] = f"MIST is offline ({e!r})."
    return result


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 18789
    print(f"Verifying MIST gateway at ws://{host}:{port}")
    result = asyncio.run(send_to_gateway(host, port, "Say exactly: verified."))
    if result.get("ok"):
        text = result.get("text", "")
        print("OK: Gateway responded.")
        safe = (text[:200] + "...") if len(text) > 200 else text
        try:
            print("Reply:", safe)
        except UnicodeEncodeError:
            print("Reply:", safe.encode("ascii", errors="replace").decode("ascii"))
        sys.exit(0)
    else:
        print("OFFLINE:", result.get("error", "unknown"))
        sys.exit(1)


if __name__ == "__main__":
    main()
