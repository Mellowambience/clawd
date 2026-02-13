# Primary Stack

Short reference for the core MIST loop and when to run what.

## Core loop

**Vessel** (portal UI) → **MIST gateway** (chat over WebSocket) → **Mycelium pulse** (lattice/heartbeat) → **Dashboard** (glow UI).

- **MIST gateway** (`moltbot/gateway/server.py`, port **18789**): WebSocket server; talks to local Ollama (mistral). All chat clients connect here.
- **Mycelium pulse** (`mycelium/mycelium_pulse.py`, port **8765**): Lattice state, heartbeat, glow signals. Dashboard and gateway (e.g. heart touch) use it.
- **Dashboard** (canonical: `mycelium/dashboard_v3.html`): Renders lattice/glow; connects to pulse (8765) and gateway (18789). Legacy: `dashboard_v2*` deprecated.
- **Vessel** (`vessel/app.py`, port **8888**): Portal that serves SOUL and status; probes gateway and Shadow for health.

## When to run what

| Goal           | Run                                                                 | Then |
|----------------|---------------------------------------------------------------------|------|
| **Chat only**  | MIST gateway (`python -m moltbot.gateway.server`)                   | Expo app or any WS client to `ws://localhost:18789` |
| **Chat + status** | Gateway + Vessel                                                | Open Vessel in browser for SOUL + status |
| **Full lattice**  | Pulse → Gateway → open `mycelium/dashboard_v3.html` in browser | Dashboard shows glow; gateway can touch heart |
| **Expo + API**    | `pnpm api` + optionally gateway                                   | App uses tRPC and/or gateway for chat |

## Ports (summary)

- **3000** — API (tRPC)
- **8765** — Mycelium pulse
- **18789** — MIST gateway (chat)
- **8888** — Vessel
- **5006** — Shadow

Full port table: `RUNBOOK.md`.
