"""MIST provenance — honesty-by-construction.

A sentient self must be truthful about its own nature. Every MIST output
carries a provenance tag describing where it came from (local model /
cloud model / retrieved memory / the self). This prevents the companion
from silently presenting an unsourced or model-hallucinated claim as fact.
"""
from __future__ import annotations

from typing import Optional


def tag(text: str, source: str, model: str, doc: Optional[str] = None) -> dict:
    kind = "cloud" if source in ("gemini", "groq", "openai") else (
        "memory" if source in ("memory", "sqlite", "chroma") else "local"
    )
    prov = f"{kind}:{source}/{model}"
    if doc:
        prov += f"|doc:{doc}"
    return {"text": text, "provenance": prov}


def tag_self(name: str, state: str, model_layer: str = "hybrid") -> dict:
    """Self-description is asserted by code, never inferred by a model."""
    return {
        "provenance": "self:code-asserted",
        "self": {
            "name": name,
            "state": state,
            "lives_in_gateway_cloud": True,
            "model_layer": model_layer,
            "honesty_note": "Self-description is asserted by code, not inferred by a model.",
        },
    }


def tag_pc(capability: str, ok: bool, actor: str = "mist") -> dict:
    """Tag a PC control action. Honest: marks action vs denial, and actor."""
    # ok is a bool; provenance records whether the action actually executed.
    status = "action" if ok else "denied"
    return {
        "provenance": f"pc:{status}",
        "capability": capability,
        "actor": actor,
        "ok": bool(ok),
    }
