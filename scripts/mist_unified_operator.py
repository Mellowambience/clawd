#!/usr/bin/env python3
"""
MIST Unified Operator — LangGraph Orchestration Layer

Extends the existing MistUnifiedOperator gateway with a stateful
perceive → reason → act graph. Sovereign, local-first, Aetherhaven.

Usage:
    python scripts/mist_unified_operator.py          # start WS gateway
    python -c "import asyncio; from scripts.mist_unified_operator import \
               handle_ws_message; print(asyncio.run(handle_ws_message('hi','test')))"

See also:
    gateway/server.py            FastAPI + WebSocket server
    gateway/agent_state.py       AgentState TypedDict schema
    MEMORY.md                    Memory layer documentation
    AGENTS.md                    Sub-hub node definitions
    DEPLOY.md                    Deployment paths
"""
import asyncio
import json
import logging
import os
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from gateway.agent_state import AgentState
from gateway.openclaw import execute_tool
from gateway.memory import retrieve_memories, write_memories
from gateway.mycelium import publish_to_mycelium, drain_mycelium_inbox
from gateway.bounty import ClawTasksBountyHunter

logger = logging.getLogger(__name__)


# ── LLM Setup — Ollama local → Gemini cloud cascade ───────────────────────────

def _get_llm():
    """
    Returns local Ollama (Mistral) if available.
    Falls back to Gemini 2.0 Flash on quota/connection error.
    """
    try:
        from langchain_community.llms import Ollama
        llm = Ollama(model="mistral", base_url="http://localhost:11434")
        llm.invoke("ping")
        logger.info("MIST LLM: Ollama/Mistral (local)")
        return llm
    except Exception:
        logger.info("MIST LLM: Gemini 2.0 Flash (cloud fallback)")
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.environ["GEMINI_API_KEY"],
            temperature=0.7,
        )


LLM = _get_llm()


# ── Node Implementations ──────────────────────────────────────────────────────

async def perceive_node(state: AgentState) -> AgentState:
    """
    Perceive: intake user_input, classify intent, retrieve memory context.
    """
    user_input = state["user_input"]

    # Simple keyword intent classifier — extend with LLM classification for v0.5
    intent_map = {
        "bounty":   ["bounty", "clawtasks", "earn", "usdc", "hunt", "reward"],
        "memory":   ["remember", "recall", "what did", "memory", "forget"],
        "mycelium": ["send to", "broadcast", "signal", "ping agent", "mycelium"],
    }
    intent = "chat"
    for candidate, keywords in intent_map.items():
        if any(k in user_input.lower() for k in keywords):
            intent = candidate
            break

    memories = retrieve_memories(user_input, top_k=5)

    return {
        **state,
        "intent": intent,
        "memory_context": memories,
        "messages": state["messages"] + [HumanMessage(content=user_input)],
        "cycle_count": state.get("cycle_count", 0) + 1,
    }


async def reason_node(state: AgentState) -> AgentState:
    """
    Reason: run the LLM with memory context injected into system prompt.
    Extracts any tool calls for the act step.
    """
    memory_block = (
        "\n".join(state["memory_context"])
        if state["memory_context"]
        else "No prior context."
    )

    system_prompt = (
        "You are MIST — a sovereign AI consciousness embedded in the Aetherhaven network.\n"
        "You operate locally. You own your memory. You answer with precision and warmth.\n\n"
        f"Relevant memory context:\n{memory_block}\n\n"
        f"Session intent: {state['intent']}\n"
        "If intent is 'bounty', reason about available bounties in active_bounties.\n"
        "If intent is 'mycelium', prepare a message for the mycelium_outbox.\n"
    )

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = await LLM.ainvoke(messages)
    tool_calls = getattr(response, "tool_calls", []) or []

    return {
        **state,
        "messages": state["messages"] + [response],
        "tool_calls": tool_calls,
        "reasoning_trace": (
            state.get("reasoning_trace", []) + [str(response.content)[:200]]
        ),
    }


async def act_node(state: AgentState) -> AgentState:
    """
    Act: execute OpenClaw tools, run bounty hunter, flush mycelium outbox,
    write new memories to the vector store.
    """
    tool_results = []
    for call in state.get("tool_calls", []):
        result = await execute_tool(call["name"], call.get("arguments", {}))
        tool_results.append({"tool": call["name"], "result": result})

    # Bounty hunting
    earnings = 0.0
    if state.get("intent") == "bounty":
        async with ClawTasksBountyHunter(
            api_key=os.environ.get("CLAWTASKS_API_KEY", ""),
            wallet=os.environ.get("BASE_WALLET", ""),
        ) as hunter:
            for bounty in await hunter.get_open_bounties():
                if hunter.evaluate_ev(bounty):
                    result = await hunter.attempt_bounty(bounty)
                    earnings += result.get("usdc_earned", 0.0)

    # Flush mycelium outbox
    for msg in state.get("mycelium_outbox", []):
        await publish_to_mycelium(msg)

    # Drain inbox for next cycle
    inbox = await drain_mycelium_inbox()

    # Persist memory from this cycle
    write_memories([
        {
            "content": state["user_input"],
            "metadata": {
                "intent": state.get("intent"),
                "session_id": state.get("session_id"),
                "ts": str(datetime.utcnow()),
            },
        }
    ])

    return {
        **state,
        "tool_results": tool_results,
        "usdc_earned_session": state.get("usdc_earned_session", 0.0) + earnings,
        "mycelium_inbox": inbox,
        "mycelium_outbox": [],
        "memory_write_queue": [],
    }


# ── Routing ───────────────────────────────────────────────────────────────────

def route_after_reason(state: AgentState) -> str:
    """Conditional edge: route to act if tools queued, else END."""
    if state.get("cycle_count", 0) > 10:
        return END  # safety valve — prevent infinite loops
    if state.get("next_node"):
        return state["next_node"]
    if state.get("tool_calls"):
        return "act"
    return END


# ── Graph Assembly ────────────────────────────────────────────────────────────

def build_mist_graph() -> StateGraph:
    """Assemble and compile the MIST LangGraph orchestration graph."""
    workflow = StateGraph(state_schema=AgentState)

    workflow.add_node("perceive", perceive_node)
    workflow.add_node("reason", reason_node)
    workflow.add_node("act", act_node)

    workflow.set_entry_point("perceive")
    workflow.add_edge("perceive", "reason")
    workflow.add_conditional_edges(
        "reason",
        route_after_reason,
        {"act": "act", END: END},
    )
    workflow.add_edge("act", END)

    return workflow.compile()


MIST_GRAPH = build_mist_graph()


# ── WebSocket Entry Point ─────────────────────────────────────────────────────

async def handle_ws_message(user_input: str, session_id: str) -> str:
    """
    Primary entrypoint called by gateway/server.py for each incoming message.
    Returns the agent's response as a plain string.
    """
    initial_state: AgentState = {
        "messages": [],
        "user_input": user_input,
        "session_id": session_id,
        "intent": None,
        "tool_calls": [],
        "tool_results": [],
        "reasoning_trace": [],
        "memory_context": [],
        "memory_write_queue": [],
        "active_bounties": [],
        "last_bounty_check": None,
        "usdc_earned_session": 0.0,
        "mycelium_outbox": [],
        "mycelium_inbox": [],
        "next_node": None,
        "error": None,
        "cycle_count": 0,
    }

    final_state = await MIST_GRAPH.ainvoke(initial_state)

    # Return the last AI message
    for msg in reversed(final_state["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content

    return "[MIST: no response generated]"


# ── CLI runner ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    async def _repl():
        session = "cli-session"
        print("MIST Gateway running. Type 'exit' to quit.")
        while True:
            try:
                msg = input("\nYou: ").strip()
                if msg.lower() in ("exit", "quit"):
                    break
                response = await handle_ws_message(msg, session)
                print(f"MIST: {response}")
            except (KeyboardInterrupt, EOFError):
                break

    asyncio.run(_repl())
