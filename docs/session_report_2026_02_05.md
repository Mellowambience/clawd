# Deep Dive Scan Report — 2026-02-05

**Scope:** Workspace scan for bugs, route conflicts, debug flags, and security exposure.

**Snapshot:** `git` dirty — modified=19, deleted=3, untracked=105

---

## Findings (Critical)
- **Token exposure**: `/config` returns a token in clear text (local-only today, but high risk if port is exposed). File: `mycelium/mycelium_pulse.py`.

## Findings (High)
- **Route collision**: Two handlers for `/` (JSON index + dashboard) cause ambiguous root behavior. File: `mycelium/mycelium_pulse.py`.
- **Asset path break**: `/dashboard/assets/*` returns 404 at runtime; dashboard now relies on `/static/app.js` as a workaround.

## Findings (Medium)
- **Debug endpoint**: `__debug_root` exposes server paths and dashboard script line; should be removed once verified.
- **Wildcard CORS**: `SocketIO(cors_allowed_origins="*")` is permissive if the service is ever exposed beyond localhost.
- **Skipped test**: `tests/auth.logout.test.ts` is `.skip`’d — logout path unverified.
- **Known bug**: Telemetry latency noted in `docs/session_report_2026_02_03.md` appears still open.

## Findings (Low / Tech Debt)
- **TODOs**: Placeholders in `drizzle/schema.ts`, `server/db.ts`, `server/routers.ts`, and `server/README.md`.
- **Version drift**: `SERVER_VERSION` in `mycelium/mycelium_pulse.py` still `2026-02-03`.
- **Workspace hygiene**: Large number of untracked files, including DBs and configs. Consider `.gitignore` updates or relocation.

---

## Recommendations
- Lock down or remove `/config` from the pulse server.
- Decide canonical behavior for `/` and remove the duplicate route.
- Either restore `/dashboard/assets/*` routing or make `/static` the official asset path.
- Remove `__debug_root` after verification.
