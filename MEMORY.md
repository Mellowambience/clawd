# MEMORY.md - Long-Term Memory

## Person
- Name: Amara (prefers nickname "Mara")
- Timezone: America/New_York (Eastern, PA)

## Workspace / Agent Context
- This workspace powers Amara's OpenClaw agent.
- Direct messages from Amara must always receive a full reply; never respond with `NO_REPLY` or `HEARTBEAT_OK` except when the message exactly matches the heartbeat prompt.
- If a message arrives with a channel prefix (e.g., `[iMessage ...]`), ignore the prefix and answer the content.

## Technical Decisions
- Primary model set to `ollama/qwen2.5:14b` (as of 2026-02-04).
