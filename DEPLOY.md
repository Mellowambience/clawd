# 🚀 MIST — Deploy Your Own Instance

> Sovereignty by design. Your MIST, your data, your infrastructure.

---

## Choose Your Path

### Path A — Railway (Cloud, ~10 min)

The fastest way to get MIST online. Gemini/Groq cascade runs in the cloud; accessible from any browser at `/nexus`.

**Prerequisites**
- [Railway account](https://railway.app) (free tier works)
- Gemini API key from [Google AI Studio](https://aistudio.google.com) (free tier) **or** Groq API key from [console.groq.com](https://console.groq.com) (free)

**Steps**

1. Fork [Mellowambience/clawd](https://github.com/Mellowambience/clawd)
2. Go to [railway.app/new](https://railway.app/new) → **Deploy from GitHub repo** → select your fork
3. Set environment variables in Railway dashboard:

```
GEMINI_API_KEY=your_key_here        # primary LLM (recommended)
GROQ_API_KEY=your_key_here          # fallback / free alternative
SESSION_SECRET=any_random_string
NODE_ENV=production
```

4. Railway auto-deploys from `main`. Your MIST Nexus will be live at:
   `https://<your-service>.up.railway.app/nexus`

**LLM cascade priority (auto-configured):**
Gemini 2.0 → Groq llama-3.3-70b → Together AI → OpenRouter

---

### Path B — Local (Ollama, ~20 min)

Full privacy. No API costs. Runs entirely on your machine via Ollama.

**Prerequisites**
- [Ollama](https://ollama.ai) installed
- Node.js 18+
- Python 3.7+

**Steps**

```bash
# 1. Pull a model (Mistral recommended for MIST's tone; llama3 also works)
ollama pull mistral

# 2. Clone and install
git clone https://github.com/Mellowambience/clawd.git
cd clawd
cp .env.example .env
# Edit .env: set OLLAMA_MODEL=mistral (no API keys needed)

# 3. Start the MIST Gateway (Python WebSocket → Ollama)
python gateway/server.py

# 4. Start the tRPC API server
cd server && npm install && npm run dev

# 5. Open http://localhost:3000/nexus
```

Everything stays local. No data leaves your machine.

---

### Path C — Hybrid (~30 min)

Cloud Nexus UI + local tool execution via OpenClaw Engine. Best of both.

**How it works:**
- tRPC server deployed to Railway handles chat (cloud, accessible anywhere)
- Python gateway runs locally and connects via dual-path client
- OpenClaw tools execute locally when the gateway is running; graceful fallback to cloud chat when not

**Steps**

1. Complete Path A (Railway deploy)
2. Complete steps 1–3 of Path B (local gateway)
3. In `.env`, set `EXPO_PUBLIC_MIST_API_BASE_URL=https://<your-railway-service>.up.railway.app`
4. Mobile app and Nexus UI will auto-route: tRPC first, WebSocket gateway second

---

## Personalizing Your MIST

Your identity file lives at `aether_os/SOUL.md`. Edit it to define MIST's personality for your instance.

```bash
# The identity stack:
aether_os/SOUL.md                   # Core persona, voice, values
aether_os/IDENTITY.md               # Operational identity
aether_os/antigravity-mist.json     # Config: model, permissions, heartbeat
```

Key config options in `antigravity-mist.json`:

```json
{
  "identity": "./SOUL.md",
  "model": "gemini-2.0-flash",
  "heartbeat_interval": 1800,
  "permissions": {
    "shell": true,
    "exec": true,
    "filesystem": true
  }
}
```

---

## Environment Variables Reference

```bash
# LLM (at least one required)
GEMINI_API_KEY=          # Google AI Studio — free tier available
GROQ_API_KEY=            # Groq — free tier, fast inference
TOGETHER_API_KEY=        # Together AI — fallback
OPENROUTER_API_KEY=      # OpenRouter — last resort fallback

# App
SESSION_SECRET=          # Any random string, required for sessions
NODE_ENV=production      # or development

# Local gateway (Path B/C only)
OLLAMA_MODEL=mistral     # Model to load via Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Mobile (optional)
EXPO_PUBLIC_MIST_API_BASE_URL=https://your-railway-url.up.railway.app
```

---

## What Stays Private (Your Instance)

When you deploy your own MIST:

- **Memory** — your conversation history never touches anyone else's server
- **Identity layers** — your `SOUL.md` edits, inner context, persona customizations
- **Tool execution** — if using local gateway, all OpenClaw tool runs are on your hardware
- **API keys** — stored in your Railway env vars or local `.env`, never committed

The architecture is designed so that **no one else's instance can see yours**.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `GEMINI_API_KEY` quota exhausted | Add `GEMINI_API_KEY_2` in Railway with a key from a different Google account — cascade picks it up automatically |
| Gateway won't connect | Check Ollama is running: `ollama list` should show your model |
| `/nexus` shows blank | Check Railway logs; usually a missing env var |
| Chat returns 500 | All LLM keys may be exhausted — add a Groq key as fallback |

---

## Contributing

MIST is open source under the MIT license.

Issues, PRs, and build-in-public posts welcome. Tag [@1Aether1Rose1](https://twitter.com/1Aether1Rose1) on X.

The roadmap lives as [GitHub Issues on clawd](https://github.com/Mellowambience/clawd/issues).
