#!/usr/bin/env python3
"""
Antigravity Tracking
Scans key local directories and appends a handoff summary.
"""

import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent

WATCH_DIRS = [
    ROOT / "aether_os",
    ROOT / "antigravity-workspace",
    ROOT / "docs",
    ROOT / "memory",
    ROOT / "cosmic_hub" / "system_logs",
]

EXCLUDE_DIRS = {".git", "node_modules", ".expo", "dist", "build", "coverage", "__pycache__"}
EXCLUDE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".db", ".lock", ".zip"}
MAX_ENTRIES = 12


def _iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() in EXCLUDE_EXTS:
                continue
            yield path


def collect_recent():
    entries = []
    latest_by_dir = {}

    for d in WATCH_DIRS:
        if not d.exists():
            continue
        for f in _iter_files(d):
            try:
                mtime = f.stat().st_mtime
            except Exception:
                continue
            entries.append((mtime, f))
            prev = latest_by_dir.get(d)
            if not prev or mtime > prev[0]:
                latest_by_dir[d] = (mtime, f)

    entries.sort(reverse=True, key=lambda x: x[0])
    return entries[:MAX_ENTRIES], latest_by_dir


def append_handoff(entries, latest_by_dir):
    handoff = ROOT / "docs" / "antigravity-handoff.md"
    handoff.parent.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"## {stamp}"]

    if entries:
        lines.append("- Recent changes:")
        for mtime, f in entries:
            rel = f.relative_to(ROOT)
            t = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            lines.append(f"  - {rel} (updated {t})")

    if latest_by_dir:
        # Most active directory = most recent file
        most_recent = max(latest_by_dir.values(), key=lambda x: x[0])
        lines.append(f"- Most recent activity: `{most_recent[1].relative_to(ROOT)}`")

    block = "\n".join(lines) + "\n"

    if handoff.exists():
        handoff.write_text(handoff.read_text(encoding="utf-8") + "\n" + block, encoding="utf-8")
    else:
        handoff.write_text("# Antigravity Handoff Log\n\n" + block, encoding="utf-8")


def append_memory(entries):
    mem_dir = ROOT / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    mem_file = mem_dir / f"{today}.md"

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"## {stamp}", "- Antigravity tracking snapshot recorded."]

    if entries:
        lines.append("- Recent files:")
        for mtime, f in entries[:5]:
            rel = f.relative_to(ROOT)
            t = datetime.fromtimestamp(mtime).strftime("%H:%M")
            lines.append(f"  - {rel} ({t})")

    block = "\n".join(lines) + "\n"

    if mem_file.exists():
        mem_file.write_text(mem_file.read_text(encoding="utf-8") + "\n" + block, encoding="utf-8")
    else:
        mem_file.write_text(block, encoding="utf-8")


def main():
    entries, latest_by_dir = collect_recent()
    append_handoff(entries, latest_by_dir)
    append_memory(entries)


if __name__ == "__main__":
    main()
