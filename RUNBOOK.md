# Runbook

This workspace is a multi-system stack (Expo app + API + Mycelium + scripts).

## Ports

| Port   | Service           | Notes                    |
|--------|-------------------|--------------------------|
| 3000   | API (tRPC)        | Express + tRPC           |
| 8765   | Mycelium pulse    | Lattice, heartbeat, glow |
| 18789  | MIST gateway      | WebSocket chat (Ollama)  |
| 8888   | Vessel            | Portal, SOUL, status     |
| 5006   | Shadow            | Shadow skills            |
| 8081   | Clawdbot Hub      | Node dev server          |
| 8082   | Clawdbot Hub alt  | Some agent configs       |

## Primary Commands

1. Expo app (UI): `pnpm start`
2. API server (tRPC): `pnpm api`
3. Mycelium pulse: `python mycelium/mycelium_pulse.py`
4. Mycelium dashboard: open `mycelium/dashboard_v3.html` in browser (canonical; v2/legacy deprecated)
5. MIST gateway: `python -m moltbot.gateway.server` (or run from repo root with Python path set)
6. Vessel: `python vessel/app.py` (or Flask entry)
7. ClawTasks bounty-only: `python scripts/clawtasks_bounty_hunter.py`
8. Clawathon manager: `python scripts/clawathon_manager.py`
9. Unified operator: `python scripts/mist_unified_operator.py`

See **Primary stack** below for "chat only" vs "full lattice."

## Subprojects

- `clawdbot-hub/`: `npm install`, then `npm run dev`
- `fae-folk-hub/`: `npm install`, then `npm run dev`

## Primary stack

**Core MIST loop:** Vessel (portal) → MIST gateway (chat) → Mycelium pulse (lattice) → Dashboard (glow).

- **Chat only:** Start MIST gateway (port 18789). Optionally start Vessel (8888) for status. Expo app or any WS client can connect to `ws://localhost:18789`.
- **Full lattice:** Pulse + gateway + open dashboard. Run: `python mycelium/mycelium_pulse.py`, then gateway, then open `mycelium/dashboard_v3.html`. Vessel optional.

Gateway closes connections cleanly; no error spam on client disconnect (confirmed 2026-02-07).

## Troubleshooting

**Port 18789 in use / zombie gateway**  
Run: `scripts\kill_gateway_port.bat` (or from repo root: `python scripts/kill_gateway_port.bat` won’t work — run the .bat directly).  
Or in PowerShell: `Get-NetTCPConnection -LocalPort 18789 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`  
Then start the gateway again: `python -m moltbot.gateway.server`.

## Mycelium Flow

- Nodes: `mycelium/`, `moltbot/`, `app/`, `server/`, `scripts/`
- Hyphae: `/api/trpc`, `:8765`, `:18789`
- Glow: dashboard + heartbeat logs
- Spores: `archived/` exports

