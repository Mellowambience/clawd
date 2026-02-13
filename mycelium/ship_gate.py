#!/usr/bin/env python3
"""One-command reliability gate for Mycelium companion runtime."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    {
        "name": "Python compile",
        "cmd": ["python", "-m", "py_compile", "mycelium/mycelium_pulse.py"],
    },
    {
        "name": "Main JS syntax",
        "cmd": ["node", "--check", "mycelium/static/dashboard/main.js"],
    },
    {
        "name": "API JS syntax",
        "cmd": ["node", "--check", "mycelium/static/dashboard/api.js"],
    },
    {
        "name": "State JS syntax",
        "cmd": ["node", "--check", "mycelium/static/dashboard/state.js"],
    },
    {
        "name": "Render JS syntax",
        "cmd": ["node", "--check", "mycelium/static/dashboard/render.js"],
    },
    {
        "name": "Guardrail module syntax",
        "cmd": ["node", "--check", "mycelium/static/dashboard/guardrail.mjs"],
    },
    {
        "name": "Companion regression tests",
        "cmd": ["python", "-m", "pytest", "mycelium/tests/test_companion_local_action.py", "-q"],
    },
    {
        "name": "Hallucination eval suite",
        "cmd": ["python", "-m", "pytest", "mycelium/tests/test_hallucination_eval_suite.py", "-q"],
    },
    {
        "name": "Guardrail logging tests",
        "cmd": ["python", "-m", "pytest", "mycelium/tests/test_guardrail_logging.py", "-q"],
    },
    {
        "name": "Gateway guardrail flow (frontend e2e-lite)",
        "cmd": ["node", "--test", "mycelium/tests_js/guardrail_flow.test.mjs"],
    },
]


def run_check(name: str, cmd: list[str]) -> int:
    print(f"[RUN] {name}: {' '.join(cmd)}")
    completed = subprocess.run(cmd, cwd=REPO_ROOT)
    if completed.returncode == 0:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name} (exit {completed.returncode})")
    return completed.returncode


def main() -> int:
    for check in CHECKS:
        code = run_check(check["name"], check["cmd"])
        if code != 0:
            print("[GATE] FAIL")
            return code
    print("[GATE] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
