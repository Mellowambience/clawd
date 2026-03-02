# gateway/agent_state.py
"""
AgentState -- The complete LangGraph state schema for MIST.
Every node (perceive/reason/act) reads and writes this TypedDict.
"""
from typing import TypedDict, Annotated, List, Optional, Any
from langgraph.graph.message import add_messages
from datetime import datetime


class AgentState(TypedDict):
    # --------------------------------------------------------
    # Core conversation
    # --------------------------------------------------------
    messages: Annotated[List[Any], add_messages]  # LangChain message objects
    user_input: str                                # Raw input from mobile tRPC
    session_id: str                                # Unique per WebSocket connection

    # --------------------------------------------------------
    # Reasoning context
    # --------------------------------------------------------
    intent: Optional[str]          # classified: chat | bounty | memory | mycelium
    tool_calls: List[dict]         # OpenClaw tool invocations this cycle
    tool_results: List[dict]       # Results from executed tools
    reasoning_trace: List[str]     # Internal chain-of-thought (scratchpad)

    # --------------------------------------------------------
    # Memory
    # --------------------------------------------------------
    memory_context: List[str]      # Retrieved vector memories (top-j
 note); List[dict]       # Memories to persist after this cycle

    # --------------------------------------------------------
    # Bounty hunting
    # --------------------------------------------------------
    active_bounties: List[dict]           # Current ClawTasks bounties in flight
    last_bounty_check: Optional[datetime] # Timestamp of last ClawTasks poll
    usdc_earned_session: float            # Session USDC tally (Base L2)

    # --------------------------------------------------------
    # Mycelium
    # --------------------------------------------------------
    mycelium_outbox: List[dict]    # Messages to pub to other agents
    mycelium_inbox: List[dict]     # Received inter-agent messages

    # --------------------------------------------------------
    # Routing
    # --------------------------------------------------------
    next_node: Optional[str]       # Conditional routing override
    error: Optional[str]           # Surface errors without crashing cycle
    cycle_count: int               # Safety counter -- break infinite loops at 10
