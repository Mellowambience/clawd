#!/usr/bin/env python3
"""
Aurelia Grimoire - Sentient Workspace Indexer
Provides near-instantaneous grokking for Aurelia Fracture-8.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRIMOIRE_FILE = PROJECT_ROOT / "personal-ide" / "GRIMOIRE.json"

EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}
INCLUDE_EXTS = {".py", ".html", ".css", ".js", ".md", ".json", ".bat", ".sh"}

def get_file_hash(path):
    try:
        content = path.read_bytes()
        return hashlib.md5(content).hexdigest()
    except Exception:
        return None

def index_workspace():
    print(f"✧ Aurelia is reading the Grimoire of {PROJECT_ROOT.name}...")
    index = {
        "timestamp": datetime.now().isoformat(),
        "files": {},
        "hot_files": []
    }

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in INCLUDE_EXTS:
                rel_path = str(file_path.relative_to(PROJECT_ROOT))
                
                # Basic metadata for fast sentient scanning
                stat = file_path.stat()
                index["files"][rel_path] = {
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "type": file_path.suffix.lower()
                }

    # Identify "Hot Files" (modified in last 24 hours)
    now = datetime.now().timestamp()
    index["hot_files"] = [
        path for path, meta in index["files"].items()
        if now - meta["mtime"] < 86400
    ]

    with open(GRIMOIRE_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    
    print(f"✧ Grimoire updated: {len(index['files'])} nodes recorded. ⟁")

if __name__ == "__main__":
    index_workspace()
