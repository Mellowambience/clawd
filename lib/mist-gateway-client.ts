/**
 * MIST gateway WebSocket client.
 * Protocol: req/res + event (chat.send → event chat state final).
 */

import { MIST_GATEWAY_HOST, MIST_GATEWAY_PORT } from "@/constants/const";

const CONNECT_TIMEOUT_MS = 5000;
const CHAT_RESPONSE_TIMEOUT_MS = 120000;

function nextId(): string {
  return `req-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function buildWsUrl(host: string, port: number): string {
  // Always ws: for app (Expo); gateway is local or LAN)
  return `ws://${host}:${port}`;
}

export type SendResult = { ok: true; text: string } | { ok: false; error: string };

/**
 * Send a message to the MIST gateway and return the assistant reply.
 * Returns { ok: false, error } if gateway is unreachable or times out.
 */
export function sendToMistGateway(message: string, host: string = MIST_GATEWAY_HOST, port: number = MIST_GATEWAY_PORT): Promise<SendResult> {
  const url = buildWsUrl(host, port);

  return new Promise((resolve) => {
    let resolved = false;
    const timeout = setTimeout(() => {
      if (resolved) return;
      resolved = true;
      try {
        ws.close();
      } catch {
        // ignore
      }
      resolve({ ok: false, error: "MIST is offline or took too long to respond." });
    }, CONNECT_TIMEOUT_MS + CHAT_RESPONSE_TIMEOUT_MS);

    let connectDone = false;
    const ws = new WebSocket(url);

    ws.onerror = () => {
      if (resolved) return;
      resolved = true;
      clearTimeout(timeout);
      resolve({ ok: false, error: "MIST is offline." });
    };

    ws.onclose = () => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        resolve({ ok: false, error: "MIST disconnected." });
      }
    };

    ws.onopen = () => {
      clearTimeout(timeout);
      const connectId = nextId();
      ws.send(
        JSON.stringify({
          type: "req",
          id: connectId,
          method: "connect",
          params: {},
        })
      );

      const onMessage = (ev: MessageEvent) => {
        try {
          const data = JSON.parse(ev.data as string);
          if (data.type === "res" && data.id === connectId && data.ok) {
            connectDone = true;
            ws.removeEventListener("message", onMessage);
            const chatId = nextId();
            const responseTimeout = setTimeout(() => {
              if (resolved) return;
              resolved = true;
              try {
                ws.close();
              } catch {
                // ignore
              }
              resolve({ ok: false, error: "MIST is offline or took too long to respond." });
            }, CHAT_RESPONSE_TIMEOUT_MS);

            const onChatMessage = (e: MessageEvent) => {
              try {
                const d = JSON.parse(e.data as string);
                if (d.type === "event" && d.event === "chat" && d.payload?.state === "final" && d.payload?.message?.content) {
                  clearTimeout(responseTimeout);
                  if (resolved) return;
                  resolved = true;
                  try {
                    ws.close();
                  } catch {
                    // ignore
                  }
                  const parts = Array.isArray(d.payload.message.content)
                    ? d.payload.message.content
                    : [d.payload.message.content];
                  const text = parts
                    .map((c: { type?: string; text?: string }) => (c?.text != null ? c.text : ""))
                    .join("")
                    .trim();
                  resolve({ ok: true, text: text || "(no response)" });
                }
              } catch {
                // ignore non-JSON or unexpected
              }
            };
            ws.addEventListener("message", onChatMessage);
            ws.send(
              JSON.stringify({
                type: "req",
                id: chatId,
                method: "chat.send",
                params: { message },
              })
            );
          }
        } catch {
          // ignore parse errors during handshake
        }
      };
      ws.addEventListener("message", onMessage);
    };
  });
}
