"""
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
