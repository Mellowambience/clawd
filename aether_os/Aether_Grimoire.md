# Aether.OS Latin Grimoire & Recovery

## Command Reference

| Command | Action | Logic |
| :--- | :--- | :--- |
| **Scrutare [Term]** | Search Web | 🟢 Gemini Speculative Search |
| **Systema Innova** | Update OS | 🟡 Sudo Apt Update |
| **Reparare (Amara_Vivat)** | **Self-Heal** | 🔴 Purges `~/.clawdbot-dev/agents/main` & Kills Port 18789 |
| **Gibberlink Audi** | Listen | 🟢 Activates Acoustic/Voice Mode |
| **Fabricare** | Build/Create | 🟢 Execute Build Commands |

## Voice Integration

**Voice Note:** Use **WhatsApp Native Voice Notes** for best STT performance.

The WhatsApp plugin is configured with `voice_notes: true` in `openclaw.json`. Simply send a voice message to your WhatsApp bot and it will automatically transcribe and process commands.

## Protocol Amara_Vivat (Self-Repair)

When the Soul becomes corrupted (infinite error loops, API key failures, or zombie processes), execute:

```bash
python repair_soul.py
```

**What it does:**
1. **Kills Zombies:** Terminates any process holding port 18789
2. **Purges Corruption:** Deletes the agent state directory that stores stale configurations
3. **Forces Re-initialization:** Next gateway start will load fresh config from `openclaw.json`

## Recovery Procedure

If the gateway is stuck in an error loop:

1. Run: `python repair_soul.py`
2. Restart: `node scripts/run-node.mjs --dev gateway --allow-unconfigured --token "secret123" --port 18789`
3. Verify: Check `http://localhost:18789` for clean startup

## Architectural Notes

- **Agent State Persistence:** Stored in `~/.clawdbot-dev/agents/main`
- **Gateway Port:** 18789
- **Configuration Source:** `openclaw.json` (or fallback to `moltbot.json`)
- **Plugin Catalog:** Links to local WhatsApp extension

---

*"Amara Vivat" - May the Soul Live*
