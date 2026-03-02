"""
MIST Memory Layer - local-first, portable.
Uses Chroma for vector storage. Fully lazy-initialized.
Export: python export_memory.py -> mist_memory_export.json
"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
_collection = None


def _get_collection():
    global _collection
    if _collection is not None:
        return _collection
    try:
        import chromadb
        from chromadb.config import Settings
        client = chromadb.Client(
            Settings(
                persist_directory=str(Path.home() / ".mist_memory"),
                anonymized_telemetry=False,
            )
        )
        _collection = client.get_or_create_collection("mist_sovereign_memory")
        return _collection
    except ImportError:
        logger.warning("chromadb not installed - memory disabled. Fix: pip install chromadb")
        return None
    except Exception as e:
        logger.warning(f"Memory store unavailable: {e}")
        return None


def retrieve_memories(query: str, top_k: int = 5) -> list[str]:
    col = _get_collection()
    if col is None:
        return []
    try:
        return col.query(query_texts=[query], n_results=top_k).get("documents", [[]])[0]
    except Exception as e:
        logger.debug(f"Memory retrieve failed: {e}")
        return []


def write_memories(entries: list[dict]) -> None:
    col = _get_collection()
    if col is None:
        return
    for i, entry in enumerate(entries):
        try:
            col.add(
                documents=[entry["content"]],
                metadatas=[entry.get("metadata", {})],
                ids=[f"mem_{abs(hash(entry['content']))}_{i}"],
            )
        except Exception as e:
            logger.debug(f"Memory write failed: {e}")
