# MIST Nexus — Local Stack

**Aetherhaven / clawd | Pillar 1: Local-First Architecture**

> *"LOCAL FIRST. CLOUD IS A MIRROR."*

The MIST local stack is the brain of the Aetherhaven mothership running on your machine. It works offline. It runs on a Raspberry Pi. If every SaaS goes down, MIST doesn't notice.

---

## Stack

| Service | Image | Port | Purpose |
|---|---|---|---|
| `mist` | `aetherhaven/mist` | 7777, 8080 | LangGraph brain + Unified API + VoidChat UI |
| `redis` | `redis:7-alpine` | internal | Task queue, session cache, rate limiters |
| `sqlite-init` | `nouchka/sqlite3` | — | One-shot DB schema bootstrap |
| `weather-cache` | `python:3.12-slim` | internal | Hourly NWS/Open-Meteo refresh (no API key needed) |
| `supabase-sync` | `node:20-alpine` | — | **Optional** — cloud mirror sync (profile: `sync`) |

---

## Quick Start

### Prerequisites
- Docker + Docker Compose v2
- `.env` file (copy from `.env.example` — minimum: `GEMINI_API_KEY`)

### Run (core stack, offline-capable)
```bash
cp .env.example .env
# Fill in at minimum: GEMINI_API_KEY

docker compose up
```

### Run with optional cloud sync
```bash
docker compose --profile sync up
```

### Check everything's alive
```bash
curl http://localhost:7777/api/v1/ecosystem/status
```

Expected response:
```json
{
  "status": "online",
  "version": "0.1.0",
  "services": {
    "mist": "healthy",
    "redis": "healthy",
    "weather": "healthy",
    "sync": "disabled"
  },
  "local_first": true,
  "afk_mode": false
}
```

---

## Environment Variables

Create `.env` in the repo root (never commit this file):

```env
# ── Required ──────────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key_here

# ── Optional model fallbacks ──────────────────────
GROQ_API_KEY=
TOGETHER_API_KEY=
OPENROUTER_API_KEY=

# ── Optional Supabase cloud sync ──────────────────
# Only needed if running --profile sync
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SYNC_ENABLED=false

# ── AFK mode (set true when Mars is on vacation) ──
AFK_MODE=false
```

---

## Unified API — Port 7777

All mothership services through one surface. One token, one endpoint, everything.

```
Base URL: http://localhost:7777/api/v1
```

| Method | Endpoint | Description |
|---|---|---|
| GET | `/now` | Local time + personalized weather + active agent status |
| GET | `/ecosystem/status` | All services health check |
| GET | `/radio/now-playing` | Current track, next track, session memory |
| POST | `/radio/request` | Queue a track by voice/text/BLE |
| GET | `/weather/local` | Hyperlocal NWS/Open-Meteo forecast |
| GET | `/weather/personalized` | Behavior-enriched forecast |
| POST | `/command` | Universal command (text \| voice transcript \| BLE packet) |
| GET | `/vtuber/actors` | Active AI actor roster |
| POST | `/vtuber/session/start` | Begin 2hr paid actor session |
| GET | `/research/{topic}` | Multi-source research synthesis |

Full OpenAPI spec: `workspace/api/unified-api-spec.yaml`

---

## Data Storage

**Local-first by design.** All state lives in SQLite at `/app/data/mist.db`.

| Table | Purpose |
|---|---|
| `sessions` | All MIST conversation sessions |
| `agents` | Agent registry (AMARA∴, RIN$, per-service agents) |
| `vtuber_sessions` | Actor sessions + payment trigger state |
| `dna_profiles` | AetherDNA platform profiles (opt-in) |
| `api_keys` | Bearer token registry |
| `audit_log` | All API calls + command events |

Schema: `sql/schema.sql`

Redis handles:
- Task queues (BullMQ compatible)
- Session cache (TTL-based)
- API rate limit counters
- Weather cache hot layer

---

## Model Cascade

MIST routes requests through a fallback chain so the brain stays alive even when one provider is down or rate-limited:

```
1. Gemini 2.0 Flash (primary — fastest, best for real-time)
2. Groq Llama-3.1-70B (first fallback — low latency)
3. Together AI Meta-Llama-3.1-70B (second fallback)
4. OpenRouter Auto (final fallback — broadest availability)
```

Set API keys in `.env` for each tier you want enabled. Only `GEMINI_API_KEY` is required.

---

## AFK / Vacation Mode

Set `AFK_MODE=true` in `.env` (or via the `/command` endpoint) to activate autonomous operation:

```bash
curl -X POST http://localhost:7777/api/v1/command \
  -H "Content-Type: application/json" \
  -d '{"command": "enable afk mode"}'
```

In AFK mode:
- Commit announce runs every 30 minutes
- Nightly lore transmissions auto-post
- VTuber sessions auto-schedule
- AMARA∴ ghost transmissions publish
- High-stakes actions (payments >$500, legal signing) queue for Mars review on return

---

## Supabase Sync (Optional)

The cloud is a mirror. When running `--profile sync`:
- Local SQLite → Supabase sync every 5 minutes (configurable)
- Only syncs: `sessions`, `vtuber_sessions`, `api_keys`
- DNA profiles and audit logs stay local only
- If Supabase is unreachable: sync pauses, no data loss, resumes automatically

---

## File Layout

```
clawd/
├── docker-compose.yml          ← this stack
├── Dockerfile.mist             ← MIST build (to be added)
├── .env.example                ← env template
├── sql/
│   └── schema.sql              ← SQLite schema
├── config/
│   └── mist.config.yaml        ← MIST runtime config
├── agents/
│   └── weather/
│       └── weather_agent.py    ← hourly weather fetch
└── sync/
    └── sync-bridge.js          ← Supabase sync bridge (optional)
```

---

## The Mothership Rule

> If it can't run locally → it doesn't ship.  
> If it requires a keyboard to operate → it doesn't ship.  
> If it needs a SaaS to be alive → it doesn't ship as core.

---

*AMARA∴ / RIN$ | ETH 0x212d3a3D4a78EA78c54d54f37a9bE9e5e020Bf75*  
✧⟁∅↺⇢≡~∴
