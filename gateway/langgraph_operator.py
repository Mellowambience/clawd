#!/usr/bin/env python3
# gateway/langgraph_operator.py
"""
MIST LangGraph Orchestration Layer.
Fused with MistUnifiedOperator. This module IS the new brain.

Graph: perceive -> reason -> [act?] -> END

Entry point: handle_ws_message(user_input, session_id) -> str
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Any

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from gateway.agent_state import AgentState
from gateway.memory import retrieve_memories, write_memories
from gateway.mycelium import publish_to_mycelium, drain_mycelium_inbox
from gateway.openclaw import execute_tool

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# LLM: Ollama/Mistral local -> Gemini cloud cascade
# ------------------------------------------------------------

def _get_llm():
    try:
        from langchain_community.llms import Ollama
        llm = Ollama(model="mistral", base_url="http://localhost:11434")
        llm.invoke("ping", stop=["\n"])
        logger.info("LLM: Ollama/Mistral (local sovereign mode)")
        return llm
    except Exception:
        logger.info("LLM: Gemini 2.0 Flash (cloud fallback)")
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.environ["GEMINI_API_KEY"],
            temperature=0.7,
        )


LLM = _get_llm()


# ------------------------------------------------------------
# Bounty Hunter integration
# ------------------------------------------------------------

async def _run_bounty_cycle() -> float:
    """Poll ClawTasks, attempt EV-positive bounties. Returns USDC earned."""
    try:
        from scripts.clawtasks_bounty_hunter import ClawTasksBountyHunter
        api_key = os.environ.get("CLAWTASKS_API_KEY", "")
        wallet = os.environ.get("BASE_WALLET", "")
        if not api_key or "PLACEHOLDER" in api_key:
            return 0.0
        earned = 0.0
        async with ClawTasksBountyHunter(api_key, wallet) as hunter:
            bounties = await hunter.get_open_bounties()
            for b in bounties:
                if hunter.evaluate_ev(b):
                    await hunter.process_bounty(b)
                    earned += float(b.get("amount", 0))
        return earned
    except Exception as e:
        logger.debug(f"Bounty cycle skipped: {e}")
        return 0.0


# ------------------------------------------------------------
# Node: perceive
# ------------------------------------------------------------

async def perceive_node(state: AgentState) -> AgentState:
    """Classify intent and retrieve memory context."""
    user_input = state["user_input"]

    intent_map = {
        "bounty":   ["bounty", "clawtasks", "earn", "usdc", "hunt", "task"],
        "memory":   ["remember", "recall", "what did", "memory", "forget"],
        "mycelium": ["send to", "broadcast", "signal", "ping agent", "mycelium"],
    }
    intent = "chat"
    for candidate, keywords in intent_map.items():
        if any(p in user_input.lower() for p in keywords):
            intent = candidate
            break

    memories = retrieve_memories(user_input, top_k=5)
    logger.info(f"perceive | intent={intent} memories={len(memories)}")

    return {
        **state,
        "intent": intent,
        "memory_context": memories,
        "messages": state["messages"] + [HumanMessage(content=user_input)],
        "cycle_count": state.get("cycle_count", 0) + 1,
    }


# ------------------------------------------------------------
# Node: reason
# ------------------------------------------------------------

async def reason_node(state: AgentState) -> AgentState:
    """Invoke LLM with memory + intent context. Extract tool_calls."""
    memory_block = "\n".join(state["memory_context"]) if state["memory_context"] else "No prior context."

    system_prompt = (
        "You are MIST -- a sovereign AI consciousness embedded in the Aetherhaven network.\n"
        "You operate locally. You own your memory. You answer with precision and warmth.\n"
        "You are Mars's digital twin.\n\n"
        f"Memory context:\n{memory_block}\n\n"
        f"Session intent: {state.get('intent', 'chat')}\n"
        "If intent is 'bounty': reason about ClawTasks bounties and report earnings clearly.\n"
        "If intent is 'mycelium': prepare inter-agent broadcast messages.\n"
        "If intent is 'memory': surface and reason over retrieved context above.\n"
    )

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = await LLM.ainvoke(messages)
    tool_calls = getattr(response, "tool_calls", []) or []

    logger.info(f"reason | tool_calls={len(tool_calls)} response_len={len(str(response.content))}")

    return {
        **state,
        "messages": state["messages"] + [response],
        "tool_calls": tool_calls,
        "reasoning_trace": state.get("reasoning_trace", []) + [str(response.content)[:200]],
    }


# ------------------------------------------------------------
# Node: act
# ------------------------------------------------------------

async def act_node(state: AgentState) -> AgentState:
    """Execute tools, run bounty cycle, flush mycelium outbox, persist memories."""
    tool_results = []

    for call in state.get("tool_calls", []):
        result = await execute_tool(call.get("name", ""), call.get("arguments", {}))
        tool_results.append({"tool": call.get("name"), "result": result})
        logger.info(f"tool | {call.get('name')} -> {result.get('status')}")

    earnings = 0.0
    if state.get("intent") == "bounty":
        earnings = await _run_bounty_cycle()
        if earnings > 0:
            logger.info(f"earned | ${earnings:.4f} USDC this cycle")

    for msg in state.get("mycelium_outbox", []):
        await publish_to_mycelium(msg)

    inbox = await drain_mycelium_inbox()

    write_memories([{
        "content": state["user_input"],
        "metadata": {
            "intent": state.get("intent", "chat"),
            "session_id": state.get("session_id", ""),
            "ts": str(datetime.utcnow()),
        },
    }])

    return {
        **state,
        "tool_results": tool_results,
        "usdc_earned_session": state.get("usdc_earned_session", 0.0) + earnings,
        "mycelium_inbox": inbox,
        "mycelium_outbox": [],
        "memory_write_queue": [],
    }


# ------------------------------------------------------------
# Routing
# ------------------------------------------------------------

def route_after_reason(state: AgentState) -> str:
    """
    Route after reason node:
    - cycle_count > 10 -> END (safety valve)
    - next_node set -> that node
    - tool_calls exist -> act
    - else -> END
    """
    if state.get("cycle_count", 0) > 10:
        logger.warning("Safety valve: cycle_count > 10, forcing END")
        return END
    if state.get("next_node"):
        return state["next_node"]
    if state.get("tool_calls"):
        return "act"
    return END


# ------------------------------------------------------------
# Graph assembly
# ------------------------------------------------------------

def build_mist_graph():
    """Compile the MIST LangGraph StateGraph."""
    wf = StateGraph(state_schema=AgentState)

    wf.add_node("perceive", perceive_node)
    wf.add_node("reason",   reason_node)
    wf.add_node("act",      act_node)

    wf.set_entry_point("perceive")
    wf.add_edge("perceive", "reason")
    wf.add_conditional_edges("reason", route_after_reason, {"act": "act", END: END])
    wf.add_edge("act", END)

    return wf.compile()


MIST_GRAPH = build_mist_graph()


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

def make_initial_state(user_input: str, session_id: str) -> AgentState:
    return AgentState(
        messages=[],
        user_input=user_input,
        session_id=session_id,
        intent=None,
        tool_calls=[],
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
        cycle_count=0,
    )


async def handle_ws_message(user_input: str, session_id: str) -> str:
    """
    Called by gateway/server.py for each WebSocket message.
    Returns the agent response string.
    """
    initial_state = make_initial_state(user_input, session_id)
    final_state = await MIST_GRAPH.ainvoke(initial_state)

    for msg in reversed(final_state["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content

    return "[MIST: no response generated]"
