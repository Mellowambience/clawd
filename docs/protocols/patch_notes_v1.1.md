# Patch Notes: Protocol Stabilization & Connectivity (v1.1)

## Summary
This patch resolves several critical "blindness" and connectivity bugs that were hindering the MIST Gateway and the Sovereign Interface.

## Root Cause Analysis
1.  **Protocol Blindness**: Tool execution results were being fed to the LLM but not broadcast to the UI websocket.
    *   *Result*: User saw MIST "act" but never saw the outcome of the action.
2.  **Handshake Regression**: `websockets` v16.0 changed the `process_request` signature to `async def (connection, request)`.
    *   *Result*: The gateway crashed with an `AttributeError` when accessed via browser, as it was using the legacy `path, headers` signature.
3.  **Process Orphans**: The use of `taskkill` in PowerShell without proper backgrounding flags caused server instances to either fail to start or collide on ports.
    *   *Result*: `CONNECTION_REFUSED` errors for the user.
4.  **Identity Dissociation**: MIST was instructed to be a "command line tool" with no chat, leading to empty responses or claims that she lacked OpenClaw capabilities.
    *   *Result*: User was told "I do not possess OpenClawd capabilities".

## Applied Patches

### [MIST Gateway]
- **Visibility Repair**: Added `tool_result` event broadcast in `server.py`. Tool outputs now appear in the chat stream.
- **Protocol Upgrade**: Updated `process_request` to be `async` and compatible with `websockets` 14.0+.
- **Identity Synthesis**: Refined `SYSTEM_PROMPT` to acknowledge MIST as the "Neural Core of the OpenClaw Engine".
- **Tool Alignment**: Mapped MIST's `run_shell` to the backend's `OpenClawEngine.execute_tool`, enabling full system command execution.

### [Mycelium Pulse]
- **Startup Stability**: Corrected startup aliases and verified listener health on port 8765.

## Verification
- [x] Dashboard Reachability (Port 8765)
- [x] Gateway Resonance (Port 18789)
- [x] Tool Output Visibility (Broadcast test)
- [x] Identity Verification (OpenClaw Query)

**Status**: SYSTEM_STABILIZED.
