# How This Project Works

One-page mental model so it doesn’t feel like a mess.

---

## Is OpenClaw part of the foundation?

**Yes.** OpenClaw is **part of the foundation** — it’s the layer that lets MIST *do* things (read files, list dirs, write, run shell, talk to Shadow). Without it, MIST can only talk; with it, MIST is agentic in your workspace. So the foundation is three pieces:

- **Ollama** (mistral): local LLM.
- **MIST gateway** (`moltbot/gateway/server.py`, port 18789): WebSocket server that talks to Ollama and runs the tool layer.
- **OpenClaw** (`moltbot/gateway/openclaw_engine.py`): the in-repo tool engine. It’s **part of the gateway**; the gateway loads it at startup. What’s *configurable* is **which** tools are enabled (e.g. shell/write via `~/.clawdbot/moltbot.json` for safety), not whether the layer exists.

The name “OpenClaw” was reused locally; there’s also an unrelated product (openclaw.ai) — ignore that for this repo.

So: **foundation = gateway + Ollama + OpenClaw (tool layer).** Optional = elevated permissions in config, and other add-ons (pulse, hubs, etc.).

---

## What actually holds everything together

```
┌─────────────────────────────────────────────────────────────────┐
│  FOUNDATION (what makes “MIST” work)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Ollama (mistral)  ←──  MIST gateway (:18789)  ←──  Any client  │
│        local              WebSocket + OpenClaw         (see below)│
│                                   (tools)                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

- **One server, one port:** The gateway is the single process that talks to Ollama and runs OpenClaw (tools). Chat + tools live here. Everything that “talks to MIST” connects here.
- **Many UIs, one pipe:** You have several front-ends (Expo app, mist_luna, Vessel, mycelium dashboards, etc.). They are **different skins** over the same pipe: `ws://localhost:18789`. That’s why it can feel messy — lots of UIs, but only one core.

---

## Why it feels messy and not cohesive

1. **Many UIs from different phases**  
   Expo app, mist_luna (Miku-style), Vessel (SOUL/status), mycelium dashboard v2/v3, personal-ide fairies, aether_os, etc. They all talk to the same gateway (or to pulse), but the repo doesn’t say “this is the main one.” So it feels scattered.

2. **Two “brains” next to the gateway**  
   - **Mycelium pulse** (8765): Lattice, heartbeat, glow. Optional for chat; needed if you want the dashboard “glow” and gateway “heart touch.”
   - **Gateway** (18789): The actual chat + tools. Required for any MIST chat.

   So you have “chat” (gateway) and “mood/telemetry” (pulse) — one foundation, one optional layer. Easy to confuse which is which.

3. **Naming overlap**  
   “Clawdbot,” “OpenClaw,” “moltbot,” “MIST,” “clawd” — different eras and layers. In this doc we use: **clawd** = this repo, **MIST** = the persona/chat, **gateway** = the one server that runs MIST, **OpenClaw** = the tool engine (part of the foundation).

4. **Optional and side stacks**  
   Clawdbot Hub, fae-folk-hub, ClawTasks bounty hunter, Shadow (5006), API (tRPC 3000) are **separate** from the core. They can integrate (e.g. OpenClaw can call Shadow for a tool) but they’re not the foundation. The foundation is gateway + Ollama + OpenClaw.

---

## One cohesive picture

| Layer            | What it is                          | Part of foundation? |
|------------------|-------------------------------------|----------------------|
| **Ollama**       | Local LLM (mistral)                 | Yes                  |
| **MIST gateway** | WebSocket server :18789, talks to Ollama, runs OpenClaw | Yes |
| **OpenClaw**     | Tool engine (read/list/write/shell, Shadow) inside gateway | Yes (what’s configurable is *which* tools are enabled) |
| **Mycelium pulse** | Lattice/heartbeat :8765            | No (for glow/dash)   |
| **Any chat UI**  | Expo, mist_luna, Vessel, dashboard, etc. | Pick one; all use gateway |

**Flow for “I want to talk to MIST (and have her do things)”:**

1. Start Ollama (with mistral).
2. Start the gateway: `python -m moltbot.gateway.server` (it loads OpenClaw with it).
3. Open **one** client (e.g. mist_luna or Expo) and connect to `ws://localhost:18789`.

That’s the minimal, cohesive path. Pulse, dashboard, Vessel, and other hubs are add-ons.

---

## If you want “one place” to look

- **Commands:** `RUNBOOK.md`
- **Ports and “chat only” vs “full lattice”:** `docs/PRIMARY_STACK.md`
- **This mental model:** `docs/HOW_THIS_PROJECT_WORKS.md`

Summary: **The project is cohesive at the core: gateway + Ollama + OpenClaw (tool layer). OpenClaw is part of that — it’s what makes MIST agentic. What’s optional is which tools are enabled in config, plus pulse/dashboards/other hubs.**
