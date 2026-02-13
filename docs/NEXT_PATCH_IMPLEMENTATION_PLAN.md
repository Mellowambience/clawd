# Next Patch — Implementation Plan

Implementation plan for the next release. Each section maps to patch-note bullets; check off as completed.

**Target scope:** One coherent patch (stability, docs, one major feature).  
**Reference:** Builds on 2026-02-07 work (gateway hardening, vessel probe, mycelium/Tauri fixes).

---

## 1. Documentation & Runbook

- [x] **Port reference** — Add a "Ports" section to `RUNBOOK.md` listing all services and ports in one place:
  - 3000 (API/tRPC), 8765 (Mycelium pulse), 18789 (MIST gateway), 8888 (Vessel), 5006 (Shadow), 8081/8082 (Clawdbot Hub)
- [x] **Primary stack doc** — Add `docs/PRIMARY_STACK.md` (or extend RUNBOOK) describing the core MIST loop: Vessel → Gateway → Pulse → Dashboard; when to run which commands for "chat only" vs "full lattice."
- [x] **README paths** — Fix `README.md` setup commands that reference `scripts/scripts/` (should be `scripts/`) so copy-paste works.

**Patch note line:** *Documentation: port reference in RUNBOOK, primary stack description, README script path fixes.*

---

## 2. Expo App ↔ MIST Gateway

- [x] **Gateway client** — In the Expo app, add a small client (e.g. in `lib/` or `constants/`) that connects to the MIST gateway over WebSocket (`ws://<host>:18789`). Use a configurable host (e.g. `localhost` for dev, env for device).
- [x] **Chat screen wiring** — Replace the mock `getAIResponse()` in `app/(tabs)/index.tsx` with:
  - Send user message to gateway via WS.
  - Receive buffered MIST response and append to messages.
  - Handle connection down / timeout (show error state or "MIST offline" message).
- [x] **Offline fallback** — When gateway is unreachable, keep current mock or a short "MIST is offline" reply so the app never blocks.

**Patch note line:** *Expo app chat now talks to MIST gateway (WebSocket :18789); fallback when gateway is offline.*

---

## 3. Stability & Cleanup

- [x] **Gateway closed-connection logs** — Confirm no remaining error spam on client disconnect (already addressed 2026-02-07; add a one-line test or note in RUNBOOK).
- [x] **Mycelium dashboard canonical** — Pick one dashboard as canonical (e.g. `dashboard_v3.html`). In RUNBOOK or PRIMARY_STACK, point "Dashboard" to that file; optionally add a short note that `dashboard_v2*` / legacy are deprecated.
- [ ] **Optional: legacy file sweep** — If time allows, move or archive `*.disabled` and duplicate dashboard backups in `personal-ide/` and `mycelium/` so the next contributor isn’t confused (low priority).

**Patch note line:** *Stability: confirmed gateway disconnect handling; documented canonical dashboard.*

---

## 4. Clawdbot Hub / Scripts (Optional for this patch)

Only include if capacity allows; otherwise defer to next patch.

- [x] **ClawTasks runner note** — In RUNBOOK, add one line: "For bounty-only: `python scripts/clawtasks_bounty_hunter.py`" (and optionally unified vs Clawathon).
- [x] **Hub enhancements** — No code change this patch; keep `docs/hub_enhancements_plan.md` and `docs/implementation_plan.md` as backlog for future patch notes.

**Patch note line:** *Runbook: added ClawTasks bounty-only command.*

---

## 5. Patch Notes Template (fill after implementation)

When the above are done, use this template for the release:

```markdown
## Patch notes — 2026-02-07

### Documentation
- Port reference and primary stack description in RUNBOOK and docs/PRIMARY_STACK.md.
- README script paths fixed (scripts/ not scripts/scripts/).

### Expo (moltbot app)
- Chat screen connected to MIST gateway (WebSocket :18789); configurable host via EXPO_PUBLIC_MIST_GATEWAY_HOST.
- Offline fallback when gateway is unavailable ("MIST is offline" message).

### Stability
- Gateway: confirmed clean disconnect handling (note in RUNBOOK).
- Documented canonical Mycelium dashboard (dashboard_v3.html); v2/legacy deprecated.

### Runbook
- ClawTasks bounty-only command and full port table added.
```

---

## Completion checklist

Before calling the patch "done":

1. [x] RUNBOOK (and optionally PRIMARY_STACK) updated.
2. [x] README setup commands run correctly.
3. [x] Expo chat sends/receives from gateway when gateway is running; fallback works when it’s not.
4. [ ] No new linter/regressions in changed files (Expo app, RUNBOOK, README).
5. [x] Patch notes section above filled with actual date and any extra bullets.
