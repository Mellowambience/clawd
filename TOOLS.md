# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Current Tool Configuration

### AI Models Available
- Ollama: llama3.3 (local)
- Qwen: coder-model, vision-model
- xAI: grok-4 (with reasoning capabilities)
- Google: gemini-2.0-flash

### Communication Channels
- Primary: WhatsApp (+13024765352)
- Gateway port: 18789

### System Access
- Elevated permissions: Enabled for WhatsApp
- Sandbox mode: Off
- Full filesystem access: Configured but requiring approval

### Workspace
- Location: C:\Users\nator\clawd
- Memory directory: C:\Users\nator\clawd\memory\
