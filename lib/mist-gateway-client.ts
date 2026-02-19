/**
 * MIST gateway client — dual-path architecture.
 *
 * Path 1 (primary): tRPC HTTP call to the Express server.
 *   Works when the server is deployed (Render, Railway, Vercel, etc.)
 *   Uses the Gemini/Forge LLM API with MIST personality.
 *
 * Path 2 (fallback): WebSocket to the local Python gateway.
 *   Works when running locally with Ollama + Python gateway.
 *   Preserves backward compatibility for local dev.
 *
 * The client tries tRPC first. If it fails (server offline, no API key),
 * it falls back to the WebSocket gateway.
 */

import {
  MIST_GATEWAY_HOST,
  MIST_GATEWAY_PORT,
  MIST_API_BASE_URL,
} from "@/constants/const";

const CONNECT_TIMEOUT_MS = 5000;
const CHAT_RESPONSE_TIMEOUT_MS = 120000;
const TRPC_TIMEOUT_MS = 30000;

function nextId(): string {
  return `req-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function buildWsUrl(host: string, port: number): string {
  return `ws://${host}:${port}`;
}

export type SendResult =
  | { ok: true; text: string }
  | { ok: false; error: string };

// ── Path 1: tRPC HTTP ────────────────────────────────────────────────────────

async function sendViaTRPC(
  message: string,
  baseUrl: string,
  sessionId?: string,
): Promise<SendResult | null> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), TRPC_TIMEOUT_MS);

    const res = await fetch(`${baseUrl}/api/trpc/chat.send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        json: { message, sessionId: sessionId || "mobile" },
      }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!res.ok) return null; // fall through to WebSocket

    const data = await res.json();
    const text = data?.result?.data?.json?.text;

    if (text) {
      return { ok: true, text };
    }

    return null; // unexpected response shape, try WebSocket
  } catch {
    return null; // tRPC unavailable, try WebSocket
  }
}

// ── Path 2: WebSocket (original gateway) ─────────────────────────────────────

function sendViaWebSocket(
  message: string,
  host: string,
  port: number,
): Promise<SendResult> {
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
      resolve({
        ok: false,
        error: "MIST is offline or took too long to respond.",
      });
    }, CONNECT_TIMEOUT_MS + CHAT_RESPONSE_TIMEOUT_MS);

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
        }),
      );

      const onMessage = (ev: MessageEvent) => {
        try {
          const data = JSON.parse(ev.data as string);
          if (data.type === "res" && data.id === connectId && data.ok) {
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
              resolve({
                ok: false,
                error: "MIST is offline or took too long to respond.",
              });
            }, CHAT_RESPONSE_TIMEOUT_MS);

            const onChatMessage = (e: MessageEvent) => {
              try {
                const d = JSON.parse(e.data as string);
                if (
                  d.type === "event" &&
                  d.event === "chat" &&
                  d.payload?.state === "final" &&
                  d.payload?.message?.content
                ) {
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
                    .map(
                      (c: { type?: string; text?: string }) =>
                        c?.text != null ? c.text : "",
                    )
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
              }),
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

// ── Public API ───────────────────────────────────────────────────────────────

/**
 * Send a message to MIST and return the assistant reply.
 *
 * Tries tRPC (HTTP) first for cloud/deployed scenarios.
 * Falls back to WebSocket for local development with Python gateway.
 */
export async function sendToMistGateway(
  message: string,
  host: string = MIST_GATEWAY_HOST,
  port: number = MIST_GATEWAY_PORT,
): Promise<SendResult> {
  // Determine tRPC base URL
  const trpcBase =
    MIST_API_BASE_URL || `http://${host}:${process.env.PORT || 3000}`;

  // Try tRPC first (works when server is deployed)
  const trpcResult = await sendViaTRPC(message, trpcBase);
  if (trpcResult) return trpcResult;

  // Fall back to WebSocket gateway (local dev with Ollama)
  return sendViaWebSocket(message, host, port);
}
