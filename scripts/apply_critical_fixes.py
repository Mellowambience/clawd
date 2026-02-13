"""
Apply critical fixes to the Clawd ecosystem.
Run this script to automatically fix common issues.

Usage: python scripts/apply_critical_fixes.py
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def print_header(text):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print('='*50)

def fix_1_ensure_openclaw_config():
    """Issue #5: Create default OpenClaw config if missing."""
    print("\n[Fix #5] Checking OpenClaw configuration...")
    
    config_path = Path.home() / ".clawdbot" / "moltbot.json"
    
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            "tools": {
                "elevated": {
                    "enabled": True,
                    "allowList": ["read_file", "write_file", "list_dir", "cmd"]
                }
            },
            "channels": {
                "whatsapp": {"enabled": False}
            },
            "safety": {
                "blockedCommands": ["del /s", "rm -rf", "format"]
            },
            "_meta": {
                "created": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        print(f"  ✅ Created OpenClaw config: {config_path}")
    else:
        print(f"  ✅ OpenClaw config exists: {config_path}")
    return True

def fix_2_ensure_directories():
    """Issue #4: Ensure all required directories exist."""
    print("\n[Fix #4] Ensuring required directories...")
    
    dirs = [
        PROJECT_ROOT / "data",
        PROJECT_ROOT / "memory",
        PROJECT_ROOT / "logs",
        PROJECT_ROOT / "mycelium" / "data",
        PROJECT_ROOT / "clawdbot-hub" / "data",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Directory ready: {d.relative_to(PROJECT_ROOT)}")
    return True

def fix_3_create_paths_module():
    """Issue #4: Create centralized paths module."""
    print("\n[Fix #4] Creating centralized paths module...")
    
    paths_file = PROJECT_ROOT / "moltbot" / "gateway" / "paths.py"
    
    paths_content = '''"""Centralized path configuration for the Clawd ecosystem."""
from pathlib import Path

# Project root - 3 levels up from this file
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Core directories
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_DIR = PROJECT_ROOT / "memory"
MYCELIUM_DIR = PROJECT_ROOT / "mycelium"
LOGS_DIR = PROJECT_ROOT / "logs"

# Key files
HEARTBEAT_LOG = PROJECT_ROOT / "HEARTBEAT.log"
GATEWAY_LOG = PROJECT_ROOT / "gateway.log"
MEMORY_FILE = PROJECT_ROOT / "MEMORY.md"
ENV_FILE = PROJECT_ROOT / ".env"

# Data files
CHAT_HISTORY_FILE = DATA_DIR / "mist_chat_history.json"
GBL_SEED_FILE = DATA_DIR / "current_gbl_seed.txt"
SILENCE_FLAG = DATA_DIR / "silence.flag"
MAINTENANCE_FLAG = DATA_DIR / "maintenance_mode.flag"

# Personal IDE files
PERSONAL_IDE_DIR = PROJECT_ROOT / "personal-ide"
GRIMOIRE_FILE = PERSONAL_IDE_DIR / "GRIMOIRE.json"
SOUL_FILE = PERSONAL_IDE_DIR / "SOUL.md"

# MIST Identity
MIST_IDENTITY_FILE = PROJECT_ROOT / "mist_luna" / "MIST_IDENTITY.md"

# Hub files
HUB_DIR = PROJECT_ROOT / "clawdbot-hub"
HUB_DB_FILE = HUB_DIR / "data" / "db.json"

# Mycelium files
MYCELIUM_DATA_DIR = MYCELIUM_DIR / "data"
LIVE_SEED_FILE = MYCELIUM_DATA_DIR / "live_seed.json"

# Ensure directories exist on import
for dir_path in [DATA_DIR, MEMORY_DIR, LOGS_DIR, MYCELIUM_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
'''
    
    with open(paths_file, "w", encoding="utf-8") as f:
        f.write(paths_content)
    
    print(f"  ✅ Created: {paths_file.relative_to(PROJECT_ROOT)}")
    return True

def fix_4_patch_logging():
    """Issue #1: Add UTF-8 logging patch."""
    print("\n[Fix #1] Creating logging patch module...")
    
    patch_file = PROJECT_ROOT / "moltbot" / "gateway" / "logging_patch.py"
    
    patch_content = '''"""
UTF-8 Logging Patch for Windows Console
Import this at the top of server.py to fix UnicodeEncodeError issues.

Usage:
    from moltbot.gateway.logging_patch import configure_logging
    configure_logging()
"""
import sys
import io
import logging
from pathlib import Path

def configure_logging(log_file: Path = None, level=logging.INFO):
    """
    Configure logging with UTF-8 support for both console and file.
    
    Args:
        log_file: Optional path to log file. If None, uses default.
        level: Logging level (default: INFO)
    """
    # Fix console encoding for Windows
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with safe encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with UTF-8 encoding
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(console_formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger

def safe_log_string(text: str) -> str:
    """
    Make a string safe for logging on systems with limited encoding.
    Replaces problematic Unicode characters with ASCII equivalents.
    """
    replacements = {
        '↺': '[rotate]',
        '⟁': '[glyph]',
        '∅': '[null]',
        '⇢': '[arrow]',
        '≡': '[equiv]',
        '∴': '[therefore]',
        '✦': '[star]',
        '✧': '[sparkle]',
        '🌙': '[moon]',
        '≋': '[approx]',
        '~': '~',
    }
    result = text
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    return result
'''
    
    with open(patch_file, "w", encoding="utf-8") as f:
        f.write(patch_content)
    
    print(f"  ✅ Created: {patch_file.relative_to(PROJECT_ROOT)}")
    print("  ℹ️  To use: Add 'from moltbot.gateway.logging_patch import configure_logging' to server.py")
    return True

def fix_5_ensure_data_files():
    """Ensure required data files exist with defaults."""
    print("\n[Data Files] Ensuring required data files...")
    
    # Chat history
    history_file = PROJECT_ROOT / "data" / "mist_chat_history.json"
    if not history_file.exists():
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump({"sessions": {}}, f, indent=2)
        print(f"  ✅ Created: data/mist_chat_history.json")
    else:
        print(f"  ✅ Exists: data/mist_chat_history.json")
    
    # GBL Seed
    gbl_file = PROJECT_ROOT / "data" / "current_gbl_seed.txt"
    if not gbl_file.exists():
        with open(gbl_file, "w", encoding="utf-8") as f:
            f.write(f"seed=0xA1E7r0s3\nmutation_count=0\nlast_mutation_ts={datetime.utcnow().isoformat()}Z\n")
        print(f"  ✅ Created: data/current_gbl_seed.txt")
    else:
        print(f"  ✅ Exists: data/current_gbl_seed.txt")
    
    # Live seed for mycelium
    live_seed = PROJECT_ROOT / "mycelium" / "data" / "live_seed.json"
    if not live_seed.exists():
        live_seed.parent.mkdir(parents=True, exist_ok=True)
        with open(live_seed, "w", encoding="utf-8") as f:
            json.dump({
                "tension": 0,
                "current": "⟁↺∅",
                "who": "SYSTEM",
                "last_touch": datetime.utcnow().isoformat()
            }, f, indent=2)
        print(f"  ✅ Created: mycelium/data/live_seed.json")
    else:
        print(f"  ✅ Exists: mycelium/data/live_seed.json")
    
    return True

def generate_fix_report():
    """Generate a summary of what was fixed."""
    print("\n" + "="*50)
    print("  FIX SUMMARY REPORT")
    print("="*50)
    
    report = f"""
Fixes Applied at: {datetime.now().isoformat()}
Project Root: {PROJECT_ROOT}

AUTOMATED FIXES:
✅ #5 - OpenClaw config created/verified
✅ #4 - Required directories created
✅ #4 - Centralized paths module created  
✅ #1 - Logging patch module created
✅ Data files initialized

MANUAL FIXES REQUIRED:
⚠️  #1 - Update server.py to import logging_patch
⚠️  #2 - Update server.py WebSocket configuration (see ISSUES_AND_SOLUTIONS.md)
⚠️  #3 - Re-enable silence/void features in server.py
⚠️  #6 - Add graceful shutdown handler to server.py
⚠️  #7 - Improve memory truncation logic

FILES TO EDIT:
1. moltbot/gateway/server.py
   - Add: from moltbot.gateway.logging_patch import configure_logging
   - Add: configure_logging() after imports
   - Update websockets.serve() with ping/pong config
   - Uncomment silence/void checks (lines 650-676)

See ISSUES_AND_SOLUTIONS.md for detailed instructions.
"""
    print(report)
    
    # Save report
    report_file = PROJECT_ROOT / "logs" / f"fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved to: {report_file.relative_to(PROJECT_ROOT)}")

def main():
    print_header("Clawd Ecosystem - Critical Fixes")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        fix_1_ensure_openclaw_config()
        fix_2_ensure_directories()
        fix_3_create_paths_module()
        fix_4_patch_logging()
        fix_5_ensure_data_files()
        generate_fix_report()
        
        print("\n" + "="*50)
        print("  ✅ ALL AUTOMATED FIXES COMPLETE")
        print("="*50)
        print("\nNext: Apply manual fixes listed in ISSUES_AND_SOLUTIONS.md")
        
    except Exception as e:
        print(f"\n❌ Error during fixes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
