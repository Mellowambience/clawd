import "dotenv/config";
import express from "express";
import { createServer } from "http";
import net from "net";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
import { registerOAuthRoutes } from "./oauth";
import { appRouter } from "../routers";
import { createContext } from "./context";
import { mountStaticRoutes } from "./static";

const allowedOrigins = (process.env.ALLOWED_ORIGINS || "")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

function isLocalOrigin(origin: string): boolean {
  try {
    const url = new URL(origin);
    return ["localhost", "127.0.0.1", "::1"].includes(url.hostname);
  } catch {
    return false;
  }
}

function isSameOriginOrTrusted(origin: string, host?: string): boolean {
  try {
    const originUrl = new URL(origin);
    if (host && originUrl.host === host) return true;
    if (originUrl.hostname.endsWith(".up.railway.app")) return true;
    return false;
  } catch {
    return false;
  }
}

function isAllowedOrigin(origin: string | undefined, host: string | undefined): boolean {
  if (!origin) return true;
  if (allowedOrigins.length > 0) {
    return allowedOrigins.includes(origin);
  }
  return isLocalOrigin(origin) || isSameOriginOrTrusted(origin, host);
}

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

// ─── SSE / Task store ────────────────────────────────────────────────────────
type SseClient = { res: express.Response; id: number };
const sseClients: Set<SseClient> = new Set();
let sseClientId = 0;
const startTime = Date.now();

interface NexusTask {
  id: string;
  type: string;
  payload: unknown;
  status: "pending" | "running" | "done" | "failed";
  createdAt: number;
}
const taskStore: NexusTask[] = [];

function broadcast(event: string, data: unknown) {
  const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const client of sseClients) {
    try {
      client.res.write(payload);
    } catch {
      sseClients.delete(client);
    }
  }
}
// ─────────────────────────────────────────────────────────────────────────────

async function startServer() {
  const app = express();
  const server = createServer(app);

  app.use((req, res, next) => {
    const origin = req.headers.origin;
    const host = req.headers.host;
    if (origin && !isAllowedOrigin(origin, host)) {
      res.status(403).json({ error: "CORS origin denied" });
      return;
    }
    if (origin) {
      res.header("Access-Control-Allow-Origin", origin);
      res.header("Vary", "Origin");
    }
    res.header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    res.header(
      "Access-Control-Allow-Headers",
      "Origin, X-Requested-With, Content-Type, Accept, Authorization",
    );
    res.header("Access-Control-Allow-Credentials", "true");

    if (req.method === "OPTIONS") {
      res.sendStatus(200);
      return;
    }
    next();
  });

  app.use(express.json({ limit: "50mb" }));
  app.use(express.urlencoded({ limit: "50mb", extended: true }));

  registerOAuthRoutes(app);

  app.get("/api/health", (_req, res) => {
    res.json({ ok: true, timestamp: Date.now(), uptime: Date.now() - startTime });
  });

  // ─── SSE stream ────────────────────────────────────────────────────────────
  app.get("/api/stream", (req, res) => {
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.setHeader("X-Accel-Buffering", "no");
    res.flushHeaders();

    const client: SseClient = { res, id: ++sseClientId };
    sseClients.add(client);

    res.write(`event: connected\ndata: ${JSON.stringify({ clientId: client.id, uptime: Date.now() - startTime })}\n\n`);

    const heartbeat = setInterval(() => {
      try {
        res.write(`event: heartbeat\ndata: ${JSON.stringify({ uptime: Date.now() - startTime, clients: sseClients.size })}\n\n`);
      } catch {
        clearInterval(heartbeat);
      }
    }, 30000);

    req.on("close", () => {
      clearInterval(heartbeat);
      sseClients.delete(client);
    });
  });

  // ─── Tasks REST ────────────────────────────────────────────────────────────
  app.get("/api/tasks", (_req, res) => {
    res.json({ tasks: taskStore });
  });

  app.post("/api/task", (req, res) => {
    const body = req.body as Partial<NexusTask>;
    const task: NexusTask = {
      id: body.id || `task-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      type: body.type || "generic",
      payload: body.payload ?? body,
      status: "pending",
      createdAt: Date.now(),
    };
    taskStore.push(task);
    broadcast("task_injected", task);
    res.json({ ok: true, task });
  });
  // ───────────────────────────────────────────────────────────────────────────

  app.use(
    "/api/trpc",
    createExpressMiddleware({
      router: appRouter,
      createContext,
    }),
  );

  // Mount web chat UI and static files (after tRPC)
  mountStaticRoutes(app);

  const preferredPort = parseInt(process.env.PORT || "3000");
  const port = await findAvailablePort(preferredPort);

  if (port !== preferredPort) {
    console.log(`Port ${preferredPort} is busy, using port ${port} instead`);
  }

  server.listen(port, () => {
    console.log(`[api] server listening on port ${port}`);
  });
}

startServer().catch(console.error);
