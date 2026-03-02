"""
MIST Gateway Test Suite
Run: pytest gateway/tests/ -v --tb=short
"""
import pytest
from gateway.agent_state import AgentState


def make_state(
    user_input: str = "hello",
    cycle_count: int = 0,
    tool_calls: list | None = None,
    intent: str | None = None,
) -> AgentState:
    return AgentState(
        messages=[],
        user_input=user_input,
        session_id="test-session",
        intent=intent,
        tool_calls=tool_calls or [],
        tool_results=[],
        reasoning_trace=[],
        memory_context=[],
        memory_write_queue=[],
        active_bounties=[],
        last_bounty_check=None,
        usdc_earned_session=0.0,
        mycelium_outbox=[],
        mycelium_inbox=[],
        next_node=None,
        error=None,
        cycle_count=cycle_count,
    )


# ── Unit tests ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_perceive_classifies_bounty_intent():
    from scripts.mist_unified_operator import perceive_node
    result = await perceive_node(make_state("find me a bounty on clawtasks"))
    assert result["intent"] == "bounty"


@pytest.mark.asyncio
async def test_perceive_classifies_memory_intent():
    from scripts.mist_unified_operator import perceive_node
    result = await perceive_node(make_state("can you recall what we discussed"))
    assert result["intent"] == "memory"


@pytest.mark.asyncio
async def test_perceive_defaults_to_chat():
    from scripts.mist_unified_operator import perceive_node
    result = await perceive_node(make_state("what is the weather today"))
    assert result["intent"] == "chat"


@pytest.mark.asyncio
async def test_perceive_increments_cycle_count():
    from scripts.mist_unified_operator import perceive_node
    result = await perceive_node(make_state(cycle_count=3))
    assert result["cycle_count"] == 4


def test_safety_valve_at_cycle_limit():
    from scripts.mist_unified_operator import route_after_reason
    from langgraph.graph import END
    state = make_state(
        cycle_count=11,
        tool_calls=[{"name": "fake_tool", "arguments": {}}],
    )
    assert route_after_reason(state) == END


def test_routes_to_act_when_tool_calls_present():
    from scripts.mist_unified_operator import route_after_reason
    state = make_state(
        cycle_count=1,
        tool_calls=[{"name": "search", "arguments": {"query": "test"}}],
    )
    assert route_after_reason(state) == "act"


def test_routes_to_end_when_no_tool_calls():
    from scripts.mist_unified_operator import route_after_reason
    from langgraph.graph import END
    state = make_state(cycle_count=1, tool_calls=[])
    assert route_after_reason(state) == END


# ── Integration tests (require LLM — mark as integration) ─────────────────────

@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_cycle_returns_string():
    """Full perceive→reason graph produces a non-empty string response."""
    from scripts.mist_unified_operator import handle_ws_message
    response = await handle_ws_message("hello mist", "test-integration-001")
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_bounty_intent_cycle():
    """Bounty intent flows through full graph without error."""
    from scripts.mist_unified_operator import handle_ws_message
    response = await handle_ws_message("hunt me a bounty", "test-integration-002")
    assert isinstance(response, str)
