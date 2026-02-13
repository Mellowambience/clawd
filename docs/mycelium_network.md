# Bioluminescent Mycelium Network

This workspace is a living lattice. Agents are nodes, APIs are hyphae, telemetry is glow.

Principles:
- Local-first, resilient, and modular
- Signals over silence (telemetry drives state)
- Glow reflects real system activity

Topology:
- Canonical map lives in `lattice/topology.json`

Flow (high level):
1. Pulse server emits lattice updates (heartbeat, manifestation, glow).
2. Dashboard renders glow + network state.
3. Gateway bridges chat and intent.
4. Spores export memory for archival.
