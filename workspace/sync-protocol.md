# Sync Protocol — clawd/MIST

## Branch Ownership

| Branch | Owner | Purpose |
|--------|-------|---------|
| `main` | Both (merge only) | Stable production code |
| `surething/updates` | SureThing | Task queue, config pushes, orchestration |
| `mist/work` | MIST / Antigravity | Feature work, skill commits |
| `upstream-sync` | SureThing | Holds upstream openclawd diffs for review |

## No-Conflict Rules

- Neither SureThing nor MIST writes directly to `main` — only merges
- Commit prefix: `[ST]` for SureThing, `[MIST]` for Antigravity
- Before starting any task, MIST should: `git pull origin surething/updates`
- Check `workspace/pending-tasks.json` before starting new work (SureThing queues here)

## Upstream Sync (secure-openclaw)

Upstream: `https://github.com/ComposioHQ/secure-openclaw`

Run `workspace/sync-upstream.sh` to pull upstream changes safely.
Protected files (see `workspace/protected-files.txt`) are **never** overwritten.

## Protected Files

See `workspace/protected-files.txt` for the full list.
These files hold MIST's identity, memory, and config — upstream changes cannot touch them.
