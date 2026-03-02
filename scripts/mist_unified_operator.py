#!/usr/bin/env python3
"""
MIST Unified Operator - entry point for CLI and legacy callers.
Delegates all graph execution to gateway/langgraph_operator.py.

Usage (WebSocket server):
    ./start.sh
    # or:
    PYTHONPATH=. python -m uvicorn gateway.server:app --port 18789

Usage (CLI REPL):
    PYTHONPATH=. python scripts/mist_unified_operator.py

See also:
    gateway/langgraph_operator.py  - canonical LangGraph brain
    gateway/server.py              - FastAPI + WebSocket
    gateway/agent_state.py         - AgentState schema
"""
import asyncio
import logging
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env", override=False)
except ImportError:
    pass

logger = logging.getLogger(__name__)


async def handle_ws_message(user_input: str, session_id: str) -> str:
    """
    Delegates to gateway.langgraph_operator.
    Lazy import avoids LLM init at module load time.
    """
    from gateway.langgraph_operator import handle_ws_message as _handle
    return await _handle(user_input, session_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def _repl():
        print("MIST Gateway REPL. Type 'exit' to quit.")
        print("(WebSocket mode: ./start.sh)\n")
        session = "cli-session"
        while True:
            try:
                msg = input("You: ").strip()
                if not msg or msg.lower() in ("exit", "quit"):
                    break
                response = await handle_ws_message(msg, session)
                print(f"MIST: {response}\n")
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye.")
                break

    asyncio.run(_repl())
