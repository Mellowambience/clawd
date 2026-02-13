"""Centralized path configuration for the Clawd ecosystem."""
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
