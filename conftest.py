# conftest.py - repo root
# Ensures pytest resolves gateway.* and scripts.* imports
# without needing pip install -e .
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
