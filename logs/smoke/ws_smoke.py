import asyncio
import json
import websockets

async def main():
    uri = "ws://127.0.0.1:18789"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "method": "chat.send",
            "id": "smoke-1",
            "params": {
                "sessionKey": "smoke",
                "message": "hello",
                "idempotencyKey": "smoke-1"
            }
        }))
        got_res = False
        got_final = False
        final_text = ""
        for _ in range(12):
            msg = await asyncio.wait_for(ws.recv(), timeout=8)
            data = json.loads(msg)
            if data.get("type") == "res" and data.get("id") == "smoke-1" and data.get("ok"):
                got_res = True
            if data.get("type") == "event" and data.get("event") == "chat":
                payload = data.get("payload", {})
                if payload.get("state") == "final":
                    got_final = True
                    content = payload.get("message", {}).get("content", [])
                    final_text = "".join([
                        c.get("text", "")
                        for c in content
                        if isinstance(c, dict) and c.get("type") == "text"
                    ])
                    break
        print(f"WS_SMOKE got_res={got_res} got_final={got_final} text_len={len(final_text)}")

asyncio.run(main())
