// server/routers/mist.ts - tRPC MIST gateway procedures
import { z } from "zod";
import { publicProcedure, router } from "../trpc";

const GATEWAY_HTTP = process.env.EXPO_PUBLIC_MIST_API_BASE_URL ?? "http://localhost:18789";
const GATEWAY_WS   = process.env.EXPO_PUBLIC_MIST_GATEWAY_WS   ?? "ws://localhost:18789/ws";

export const mistRouter = router({
  chat: publicProcedure
    .input(z.object({ message: z.string(), sessionId: z.string() }))
    .mutation(async ({ input }) => {
      const res = await fetch(`${GATEWAY_HTTP}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input.message, session_id: input.sessionId }),
      });
      if (!res.ok) throw new Error(`MIST gateway error: ${res.status}`);
      return { reply: (await res.json()).response as string };
    }),

  stream: publicProcedure
    .input(z.object({ message: z.string(), sessionId: z.string() }))
    .subscription(async function* ({ input }) {
      const ws = new WebSocket(GATEWAY_WS);
      await new Promise<void>((res, rej) => { ws.onopen = () => res(); ws.onerror = rej; });
      ws.send(JSON.stringify({ message: input.message, session_id: input.sessionId }));
      const buf: string[] = [];
      ws.onmessage = (e) => buf.push(e.data as string);
      while (ws.readyState !== WebSocket.CLOSED) {
        if (buf.length > 0) yield { chunk: buf.shift()! };
        else await new Promise((r) => setTimeout(r, 50));
      }
    }),

  health: publicProcedure.query(async () => {
    try {
      const res = await fetch(`${GATEWAY_HTTP}/health`, { signal: AbortSignal.timeout(3000) });
      return { ok: res.ok };
    } catch { return { ok: false }; }
  }),
});
