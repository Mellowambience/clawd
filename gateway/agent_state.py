"""
MIST AgentState — canonical TypedDict for the LangGraph orchestration loop.
Every node in the MIST graph reads from and writes to this schema.
"""
from typing import TypedDict, Annotated, List, Optional, Any
from langgraph.graph.message import add_messages
from datetime import datetime


class AgentState(TypedDict):
    # ── Core conversation ──────────────────────────────────────────────────
    messages: Annotated[List[Any], add_messages]  # LangChain message objects
    user_input: str                                # raw input from tRPC / WS
    session_id: str                                # unique per WebSocket conn

    # ── Reasoning context ─────────────────────────────────────────────────
    intent: Optional[str]      # classified: chat | bounty | memory | mycelium
    tool_calls: List[dict]     # OpenClaw tool invocations this cycle
    tool_results: List[dict]   # results from executed tools
    reasoning_trace: List[str] # internal scratchpad (not exposed to user)

    # ── Memory ────────────────────────────────────────────────────────────
    memory_context: List[str]      # retrieved vector memories (top-k)
    memory_write_queue: List[dict] # memories to persist after this cycle

    # ── Bounty hunting ────────────────────────────────────────────────────
    active_bounties: List[dict]           # ClawTasks bounties in flight
    last_bounty_check: Optional[datetime] # timestamp of last poll
    usdc_earned_session: float            # session USDC tally (Base L2)

    # ── Mycelium inter-agent comms ────────────────────────────────────────
    mycelium_outbox: List[dict]  # messages to publish to sibling agents
    mycelium_inbox: List[dict]   # messages received from sibling agents

    # ── Routing & safety ─────────────────────────────────────────────────
    next_node: Optional[str]  # conditional routing override
    error: Optional[str]      # surface errors without crashing cycle
    cycle_count: int          # safety counter — break infinite loops at >10
