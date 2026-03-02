# gateway/tests/test_graph.py
import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import AIMessage
from langgraph.graph import END

from gateway.langgraph_operator import perceive_node, route_after_reason, make_initial_state


def make_state(user_input="hello", cycle_count=0, tool_calls=None, next_node=None):
    s = make_initial_state(user_input, "test")
    s["cycle_count"] = cycle_count
    s["tool_calls"] = tool_calls or []
    s["next_node"] = next_node
    return s


@pytest.mark.asyncio
@patch("langgraph_operator.retrieve_memories", return_value=[])
async def test_perceive_bounty_intent(mock_mem):
    result = await perceive_node(make_state("find me a bounty"))
    assert result["intent"] == "bounty"


@pytest.mark.asyncio
@patch("langgraph_operator.retrieve_memories", return_value=[])
async def test_perceive_chat_default(mock_mem):
    result = await perceive_node(make_state("hello mist"))
    assert result["intent"] == "chat"


def test_safety_valve():
    assert route_after_reason(make_state(cycle_count=11, tool_calls=[{"name": "x"}])) == END


def test_routes_to_act_with_tools():
    assert route_after_reason(make_state(tool_calls=[{"name": "search"}])) == "act"


def test_routes_to_end_no_tools():
    assert route_after_reason(make_state()) == END


@pytest.mark.asyncio
@patch("langgraph_operator.retrieve_memories", return_value=[])
@patch("langgraph_operator.write_memories")
@patch("langgraph_operator.LLM")
async def test_full_cycle(mock_llm, mock_write, mock_mem):
    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content="MIST sovereign response."))
    from gateway.langgraph_operator import handle_ws_message
    response = await handle_ws_message("hello", "sess-001")
    assert isinstance(response, str) and len(response) > 0
