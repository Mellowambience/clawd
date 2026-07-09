"""
MIST / clawd — PC Inventory (host self-awareness)

Exposes what the sovereign gateway box can actually do, so MIST can reason
about its own capacity (e.g. whether Ollama can load a given model, which
runtimes are present, what ports are already bound).

Stdlib-only on purpose: runs on the gateway without pip installs.
Optional `psutil` is used if present for richer memory/process data, but the
module degrades gracefully without it.

Public API:
    get_inventory() -> dict          # full host manifest
    can_run_model(gguf_bytes) -> bool # rough headroom check for Ollama
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone


def _run(cmd):
    """Run a command, return stripped stdout or '' on any failure."""
    try:
        out = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=8
        )
        return out.stdout.strip()
    except Exception:
        return ""


def _cpu():
    info = {
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "cores_physical": os.cpu_count() or 0,
        "system": platform.system(),
        "release": platform.release(),
        "python": platform.python_version(),
    }
    # Try to enrich with a human-readable CPU name (best-effort, OS-specific)
    if platform.system() == "Windows":
        name = _run(
            'wmic cpu get Name /value 2>nul'
        ).replace("Name=", "").strip().splitlines()
        if name:
            info["model"] = name[0].strip()
    elif platform.system() == "Linux":
        model = _run("cat /proc/cpuinfo 2>/dev/null | grep -m1 'model name'")
        if model:
            info["model"] = model.split(":", 1)[-1].strip()
    elif platform.system() == "Darwin":
        info["model"] = _run("sysctl -n machdep.cpu.brand_string 2>/dev/null")
    return info


def _ram_bytes():
    """Best-effort total RAM in bytes. Returns 0 if unknown."""
    try:
        import psutil  # type: ignore
        return psutil.virtual_memory().total
    except Exception:
        pass
    system = platform.system()
    if system == "Linux":
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        return int(line.split()[1]) * 1024
        except Exception:
            return 0
    if system == "Darwin":
        out = _run("sysctl -n hw.memsize 2>/dev/null")
        return int(out) if out.isdigit() else 0
    if system == "Windows":
        out = _run('wmic ComputerSystem get TotalPhysicalMemory /value 2>nul')
        digits = "".join(c for c in out if c.isdigit())
        return int(digits) if digits else 0
    return 0


def _gpu():
    """Detect NVIDIA/AMD GPUs via vendor CLIs; generic otherwise."""
    gpus = []
    # NVIDIA
    nvidia = _run("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null")
    if nvidia:
        for line in nvidia.splitlines():
            if line.strip():
                name, _, mem = line.partition(",")
                gpus.append({"vendor": "nvidia", "name": name.strip(),
                             "vram": mem.strip()})
    # AMD on Linux
    amd = _run("rocminfo 2>/dev/null | grep -m1 'Marketing Name'")
    if amd and not gpus:
        gpus.append({"vendor": "amd", "name": amd.split(":", 1)[-1].strip()})
    # Apple
    if platform.system() == "Darwin":
        gpus.append({"vendor": "apple", "name": "Apple Silicon (unified)" })
    return gpus or [{"vendor": "unknown", "name": "no GPU detected"}]


def _drives():
    """List mounted volumes with free/total bytes."""
    drives = []
    system = platform.system()
    if system == "Windows":
        roots = [f"{c}:\\" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                 if os.path.exists(f"{c}:\\")]
    else:
        roots = ["/"]
        # add common extra mounts if present
        for p in ("/data", "/mnt", "/home"):
            if os.path.exists(p):
                roots.append(p)
    for r in roots:
        try:
            total, used, free = shutil.disk_usage(r)
            drives.append({"mount": r, "total_gb": round(total / 1e9, 1),
                           "free_gb": round(free / 1e9, 1)})
        except Exception:
            continue
    return drives


def _runtimes():
    """Detect installed AI/dev runtimes by querying their --version."""
    checks = {
        "ollama": "ollama --version",
        "python": f"{sys.executable} --version",
        "node": "node --version",
        "git": "git --version",
        "gh": "gh --version",
        "docker": "docker --version",
        "cuda": "nvcc --version",
    }
    found = {}
    for name, cmd in checks.items():
        out = _run(cmd)
        if out:
            # take the first non-empty line, trimmed
            first = next((l.strip() for l in out.splitlines() if l.strip()), out)
            found[name] = first
    return found


def _open_ports():
    """List listening TCP ports (best-effort, OS-specific)."""
    system = platform.system()
    ports = []
    if system == "Windows":
        out = _run('netstat -ano -p TCP 2>nul | findstr LISTENING')
    else:
        out = _run("ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null")
    for line in out.splitlines():
        # crude: grab a :port just before the end or in the local addr
        toks = line.split()
        for tok in toks:
            if ":" in tok:
                port = tok.rsplit(":", 1)[-1]
                if port.isdigit() and int(port) > 0:
                    ports.append(int(port))
    return sorted(set(ports))


def get_inventory():
    """Return the full host manifest dict."""
    ram = _ram_bytes()
    inv = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "os": _cpu(),
        "ram_total_gb": round(ram / 1e9, 1) if ram else 0,
        "gpus": _gpu(),
        "drives": _drives(),
        "runtimes": _runtimes(),
        "open_ports": _open_ports(),
    }
    return inv


def can_run_model(gguf_bytes: int) -> bool:
    """
    Rough headroom check: can the gateway load a GGUF of this size?

    Rule of thumb: a quantized model needs ~ (file size * 1.5) of free RAM
    (weights + KV cache + overhead). Returns False if RAM is unknown or tight.
    """
    inv = get_inventory()
    free_ram = inv.get("ram_total_gb", 0)
    if not free_ram:
        return False
    needed_gb = (gguf_bytes / 1e9) * 1.5
    return free_ram >= needed_gb


if __name__ == "__main__":
    print(json.dumps(get_inventory(), indent=2))
