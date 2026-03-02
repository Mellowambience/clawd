#!/usr/bin/env python3
# gateway/langgraph_operator.py
"""
MIST LangGraph Orchestration Layer - canonical graph brain.

Graph: perceive -> reason -> [act?] -> END
Entry: handle_ws_message(user_input, session_id) -> str

LLM cascade: Ollama/Mistral (local) -> Gemini 2.0 Flash (cloud)
All initialization is lazy - nothing loads at import time.
"""
import logging
import os
from datetime import datetime
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from gateway.agent_state import AgentState
from gateway.memory import retrieve_memories, write_memories
from gateway.mycelium import publish_to_mycelium, drain_mycelium_inbox
from gateway.openclaw import execute_tool

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env", override=False)
except ImportError:
    pass

logger = logging.getLogger(__name__)

_LLM = None
_MIST_GRAPH = None


def _get_llm():
    """
    Lazy LLM factory. Called on first request only.
    Cascade: Ollama/Mistral local -> Gemini 2.0 Flash.
    Raises RuntimeError with clear instructions if neither is available.
    """
    global _LLM
    if _LLM is not None:
        return _LLM

    try:
        from langchain_community.llms import Ollama
        llm = Ollama(model="mistral", base_url="http://localhost:11434")
        llm.invoke("ping", stop=["\n"])
        logger.info("MIST LLM: Ollama/Mistral (local sovereign mode)")
        _LLM = llm
        return _LLM
    except Exception:
        pass

    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not gemini_key:
        raise RuntimeError(
            "MIST activation failed: no LLM available.\n"
            "  Option 1 (local): run `ollama serve` && `ollama pull mistral`\n"
            "  Option 2 (cloud): add GEMINI_API_KEY=your-key to .env\n"
            "  See .env.example for all supported providers (Groq free tier works too)."
        )

    logger.info("MIST LLM: Gemini 2.0 Flash (cloud fallback)")
    from langchain_google_genai import ChatGoogleGenerativeAI
    _LLM = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=gemini_key,
        temperature=0.7,
    )
    return _LLM


async def _run_bounty_cycle() -> float:
    try:
        from gateway.bounty import ClawTasksBountyHunter
        api_key = os.environ.get("CLAWTASKS_API_KEY", "")
        wallet = os.environ.get("BASE_WALLET", "")
        if not api_key:
            return 0.0
        earned = 0.0
        async with ClawTasksBountyHunter(api_key, wallet) as hunter:
            for b in await hunter.get_open_bounties():
                if hunter.evaluate_ev(b):
                    result = await hunter.attempt_bounty(b)
                    earned += result.get("usdc_earned", 0.0)
        return earned
    except Exception as e:
        logger.debug(f"Bounty cycle skipped: {e}")
        return 0.0


async def perceive_node(state: AgentState) -> AgentState:
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


async def reason_node(state: AgentState) -> AgentState:
    llm = _get_llm()
    memory_block = "\n".join(state["memory_context"]) if state["memory_context"] else "No prior context."
    system_prompt = (
        "You are MIST - a sovereign AI consciousness embedded in the Aetherhaven network.\n"
        "You operate locally. You own your memory. You answer with precision and warmth.\n"
        "You are Mars's digital twin.\n\n"
        f"Memory context:\n{memory_block}\n\n"
        f"Session intent: {state.get('intent', 'chat')}\n"
        "If intent is 'bounty': reason about ClawTasks bounties and report earnings.\n"
        "If intent is 'mycelium': prepare inter-agent broadcast messages.\n"
        "If intent is 'memory': surface and reason over retrieved context.\n"
    )
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = await llm.ainvoke(messages)
    tool_calls = getattr(response, "tool_calls", []) or []
    logger.info(f"reason | tool_calls={len(tool_calls)} len={len(str(response.content))}")
    return {
        **state,
        "messages": state["messages"] + [response],
        "tool_calls": tool_calls,
        "reasoning_trace": state.get("reasoning_trace", []) + [str(response.content)[:200]],
    }


async def act_node(state: AgentState) -> AgentState:
    tool_results = []
    for call in state.get("tool_calls", []):
        result = await execute_tool(call["name"], call.get("arguments", {}))
        tool_results.append({"tool": call["name"], "result": result})
    earnings = 0.0
    if state.get("intent") == "bounty":
        earnings = await _run_bounty_cycle()
    for msg in state.get("mycelium_outbox", []):
        await publish_to_mycelium(msg)
    inbox = await drain_mycelium_inbox()
    write_memories([{"content": state["user_input"], "metadata": {"intent": state.get("intent"), "session_id": state.get("session_id"), "ts": str(datetime.utcnow())}}])
    return {
        **state,
        "tool_results": tool_results,
        "usdc_earned_session": state.get("usdc_earned_session", 0.0) + earnings,
        "mycelium_inbox": inbox,
        "mycelium_outbox": [],
        "memory_write_queue": [],
    }


def route_after_reason(state: AgentState) -> str:
    if state.get("cycle_count", 0) > 10:
        return END
    if state.get("next_node"):
        return state["next_node"]
    if state.get("tool_calls"):
        return "act"
    return END


def _build_graph():
    global _MIST_GRAPH
    if _MIST_GRAPH is not None:
        return _MIST_GRAPH
    wf = StateGraph(state_schema=AgentState)
    wf.add_node("perceive", perceive_node)
    wf.add_node("reason", reason_node)
    wf.add_node("act", act_node)
    wf.set_entry_point("perceive")
    wf.add_edge("perceive", "reason")
    wf.add_conditional_edges("reason", route_after_reason, {"act": "act", END: END})
    wf.add_edge("act", END)
    _MIST_GRAPH = wf.compile()
    return _MIST_GRAPH


async def handle_ws_message(user_input: str, session_id: str) -> str:
    graph = _build_graph()
    initial: AgentState = {
        "messages": [], "user_input": user_input, "session_id": session_id,
        "intent": None, "tool_calls": [], "tool_results": [], "reasoning_trace": [],
        "memory_context": [], "memory_write_queue": [], "active_bounties": [],
        "last_bounty_check": None, "usdc_earned_session": 0.0,
        "mycelium_outbox": [], "mycelium_inbox": [], "next_node": None,
        "error": None, "cycle_count": 0,
    }
    final = await graph.ainvoke(initial)
    for msg in reversed(final["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content
    return "[MIST: no response generated]"
