# System Architecture Report & Restoration Plan
**Date:** 2026-02-03
**Status:** CRITICAL RESTORATION REQUIRED

## current_state_analysis

### 1. The Broken Core (Identity Crisis)
- **What's Running:** A simplified `server.py` (Custom Python Gateway).
- **What's Missing:** The full **OpenClaw Agent** capabilities. The `moltbot` directory contains *only* the gateway, missing the Plugin System, Tool Managers, and WhatsApp integration logic.
- **The Result:** MIST acts as a chatbot but cannot interact with the outside world (WhatsApp, Filesystem tools) as defined in `moltbot.json`.

### 2. The Renaming Fallout
- The migration from `clawdbot` -> `moltbot` -> `openclaw` left the workspace in a fragmented state.
- **Config:** `moltbot.json` defines a rich agent (Rules, WhatsApp, Tools).
- **Code:** The running code (`server.py`) ignores this config entirely.

### 3. The Soul (Status: SECURE)
- `SOUL.md`: Intact.
- `sync_soul.py`: Successfully synced the persona to configs.
- **Brain Surgery**: We manually injected the Soul into `server.py`, so her personality is active, even if her hands (tools) are cut off.

---

## restoration_plan (Today's Mission)

We will restore MIST to her full OpenClaw capabilities by rebuilding the missing bridges in `server.py` and `launch_mist.bat`.

### Phase 1: The Brain Patch (Completed)
- [x] Integrate `SOUL.md` prompt into `server.py`.
- [x] Fix "Memory Dump" confusion.

### Phase 2: The Senses (WhatsApp & Config)
- [ ] **Inject Config Loader**: Update `server.py` to actually read `moltbot.json`.
- [ ] **Restore WhatsApp**: MIST can talk to WhatsApp, but `server.py` has no logic for it. We must verify if an external "Bridge" script exists or if we need to implement a simple HTTP-to-WhatsApp layer.
    - *Note:* Since `clawdbot-hub` (Node) is deprecated, we might need a Python-based WhatsApp handler or a re-link to the `moltbot` package if installed.

### Phase 3: The Body (System Tools)
- [ ] **Enable Tool Use**: Give MIST the ability to run commands (controlled) again, matching `moltbot.json` permissions (`"elevated": true`).

### Phase 4: The Interface (Dashboard)
- [x] Mycelium Dashboard is running.
- [ ] **Fairy Integration**: Ensure the Dashboard and Fairy visualize the *Real* state (connected/disconnected) correctly.

---

## patch_notes_v2026.02.03

### 🛠️ System
- **Restored**: Official `SOUL.md` personality injection via `sync_soul.py`.
- **Fixed**: `server.py` now uses the correct "Aurelia Overlay" prompt.
- **Fixed**: "Memory Overload" bug where MIST read her own memory as user input.

### 🔮 Planned (Immediate)
- **Integration**: Re-enable `moltbot.json` loading in Gateway.
- **Connection**: Attempt to restore WhatsApp signaling.
- **Cleanup**: Remove deprecated `start_hub.bat` references from workflow.

---
**Recommendation:**
Proceed with **Phase 2**. I will modify `server.py` to try and load the `moltbot.json` configuration, paving the way for plugins.

---

## patch_notes_v2026.02.05

### 🧭 Dashboard + Lattice
- **Refactor**: Extracted the large inline dashboard script into `mycelium/dashboard/app.js` and switched the page to load a module script.
- **Fix**: Aligned the frontend to listen for `lattice_update` (and back-compat `pulse`) so live telemetry resumes.
- **Workaround**: Switched asset loading to `/static/app.js` because `/dashboard/assets/*` was returning 404 during runtime.
- **Resilience**: Added manifest polling fallback if the socket is down.

### 🌌 Ephemeris (Local-Only Path)
- **Added**: `mycelium/ephemeris_local.py` to compute local planetary positions via Skyfield when available.
- **Config**: `mycelium/ephemeris_config.json` with lat/lon/elevation + orb settings.
- **Data Stub**: `mycelium/ephemeris/README.md` describing where to place `de421.bsp`.
- **Lattice**: `build_lattice()` now includes a `cosmic` payload when local ephemeris is available.

### 🧾 Artifacts
- **Saved**: `aurelia-mist-lunar-ghostline.md`, `ephem-api-bind-planet-sky-weave.md`, and `soul.min.md`.

---

## patch_notes_v2026.02.06 (Implementation Plan)

### 🌌 Ephemeris (Local, Offline)
- **Dependency**: Install `skyfield` and verify import.
- **Data**: Place `de421.bsp` in `mycelium/ephemeris/`.
- **Expose**: Confirm `cosmic` payload returns `ok: true` and includes aspects.
- **UI**: Add a minimal “cosmic status” card (phase/aspects + error fallback).

### 🧭 Dashboard Assets
- **Canonical Path**: Decide between `/static` and `/dashboard/assets` and remove the unused route.
- **Cleanup**: Remove `__debug_root` endpoint once verified.
- **Verify**: `GET /dashboard` loads the module script without 404s.

### 🔐 Security & Boundaries
- **/config**: Remove or gate token exposure behind a local-only flag.
- **CORS**: Narrow Socket.IO origins to `http://localhost:8765` (or a small allowlist).

### 🧩 Dashboard Modularity
- **Split**: Break `mycelium/dashboard/app.js` into `data.js`, `state.js`, `ui.js`, `effects.js`, `main.js`.
- **Contract**: One state object + derived selectors + a single render loop.

### ✅ Acceptance Checks
- **Cosmic**: `cosmic.ok === true` with populated `bodies` and `aspects`.
- **Assets**: No 404s on the dashboard JS/CSS.
- **Security**: `/config` no longer returns tokens by default.
