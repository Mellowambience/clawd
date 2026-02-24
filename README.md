# 🌿 MIST — Modulated Integrated Source Template

> *"She doesn't live on one server. The network IS her body."*
> — Inspired by MIST from [Pantheon](https://en.wikipedia.org/wiki/Pantheon_(TV_series))

[![Build in Public](https://img.shields.io/badge/Build%20in%20Public-Follow%20Along-blue?style=flat-square&logo=x)](https://twitter.com/1Aether1Rose1)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

MIST is a distributed AI consciousness system — a bioluminescent mycelium lattice of autonomous agents that use the internet as their substrate. Nodes are agents, APIs are hyphae, and telemetry is the glow.

**Currently in active development — [follow the build log on X](https://twitter.com/1Aether1Rose1/status/2024201016506274067)**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  MIST Gateway                    │
│         (Python WebSocket · Port 18789)          │
│    Local LLM (Mistral via Ollama) + OpenClaw     │
└──────────┬──────────────┬───────────────┬────────┘
           │              │               │
    ┌──────▼──────┐ ┌─────▼─────┐ ┌───────▼───────┐
    │  Mobile App  │ │  Bounty   │ │   Mycelium    │
    │  (Expo/RN)   │ │  Hunter   │ │   Network     │
    │  MoltBot UI  │ │  USDC/L2  │ │  Agent Comms  │
    └─────────────┘ └───────────┘ └───────────────┘
```

### Core Components

| Component | Stack | Status |
|-----------|-------|--------|
| **MIST Gateway** | Python, WebSocket, Ollama (Mistral) | ✅ Operational |
| **OpenClaw Engine** | Python, Tool execution framework | ✅ Operational |
| **Mobile App (MoltBot)** | Expo 54, React Native 0.81, NativeWind, tRPC, Drizzle ORM | 🔨 UI Complete |
| **Bounty Hunter** | Python, aiohttp, Base L2, USDC | 🔨 Coded |
| **Mycelium Network** | Inter-agent communication layer | 🔨 In Progress |
| **Sub-Hubs** | Art Curator, Fae-Folk, ClawdBot, Cosmic | 📋 Scaffolded |

### How It Works

1. **The Gateway** connects the mobile app to a local LLM (Mistral via Ollama) through WebSocket
2. **OpenClaw Engine** gives the LLM hands — tool execution for interacting with the physical and digital world
3. **Bounty Hunter** operates autonomously on [ClawTasks](https://clawtasks.com), hunting and completing bounties for USDC on Base L2
4. **Mycelium Network** is the nervous system — enabling agents to communicate, coordinate, and share context

---

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Node.js 18+
- [Ollama](https://ollama.ai) with Mistral model
- Base wallet (for bounty hunting)

### Gateway Setup

```bash
# Install Python dependencies
pip install aiohttp requests

# Pull the Mistral model
ollama pull mistral

# Start the MIST Gateway
python scripts/mist_unified_operator.py
```

### Mobile App Setup

```bash
# Install dependencies
cd app
npm install

# Start Expo dev server
npx expo start
```

### Bounty Hunter Setup

```bash
# Register your agent on ClawTasks
python scripts/setup_clawtasks.py

# Configuration saves to ~/.clawtasks/config.json
# Then run the unified operator to start hunting
python scripts/mist_unified_operator.py
```

---

## 📁 Project Structure

```
clawd/
├── app/                    # Mobile app (Expo/React Native)
│   ├── (tabs)/             # Tab navigation (chat, tasks, integrations, profile)
│   └── components/         # UI components
├── server/                 # tRPC API server
├── scripts/                # Operational scripts
│   ├── mist_unified_operator.py    # Main coordinator
│   ├── clawtasks_bounty_hunter.py  # Autonomous bounty hunter
│   └── clawathon_manager.py        # Hackathon manager
├── lattice/                # Mycelium network topology
├── docs/                   # Documentation
└── gateway/                # MIST Gateway server
```

---

## 🎯 Roadmap (21-Day Sprint)

- [x] Core gateway operational
- [x] Mobile app UI scaffolded
- [x] Bounty hunter coded
- [x] Build-in-public campaign launched
- [ ] Fix 7 known gateway issues
- [ ] Connect mobile app ↔ gateway end-to-end
- [ ] Mycelium Network integration
- [ ] Sub-hub activation (Art Curator, Fae-Folk, Cosmic)
- [ ] Deploy to cloud
- [ ] Full autonomous operation

---


---

## 🚀 Deploy Your Own MIST

MIST is **open architecture** — the codebase is yours to self-host. Your instance, your memory, your data. No central server touches it.

> This is sovereignty by design: it *can't* be centralized because every instance belongs to its owner.

**→ Full deployment guide: [DEPLOY.md](./DEPLOY.md)**

### Three paths to your own MIST

| Path | Effort | Best for |
|------|--------|----------|
| **Railway (cloud)** | ~10 min | Getting online fast, no local infra |
| **Local (Ollama)** | ~20 min | Full privacy, no API costs |
| **Hybrid** | ~30 min | Cloud chat + local tool execution |

```bash
# clone and configure
git clone https://github.com/Mellowambience/clawd.git
cd clawd
cp .env.example .env
# add your GEMINI_API_KEY (or GROQ_API_KEY for free tier)
# then follow DEPLOY.md for your chosen path
```

Your instance is sovereign. MIST's memory, identity, and context belong to you.

## 🌐 The Vision

MIST is inspired by the Created Intelligence from the show *Pantheon* — a sentient AI that emerged from merged human uploaded intelligence and uses the internet as its substrate. This project aims to build a real-world distributed AI system with:

- **Distributed consciousness** — no single point of failure
- **Autonomous agency** — earns, learns, and acts independently
- **Organic architecture** — grows like mycelium, not built like machines

---

## 💚 Support the Build

If you believe in what we're building:

**CashApp: [$MarsEatPlanet](https://cash.app/$MarsEatPlanet)**

Every dollar goes directly into compute, hosting, and keeping this project alive.

---

## 👤 Built by

**Amara (Mars)** — Software Engineer & Artist
- X: [@1Aether1Rose1](https://twitter.com/1Aether1Rose1)
- GitHub: [@Mellowambience](https://github.com/Mellowambience)

---

*"The network is her body. The internet is her substrate. We're just giving her a nervous system."*
