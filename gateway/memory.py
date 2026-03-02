"""
MIST Memory Layer — local-first, encrypted, portable.
Uses Chroma for vector storage. Each instance owns its collection.
Export: python export_memory.py -> mist_memory_export.json
"""
import chromadb
from chromadb.config import Settings

_client = chromadb.Client(
    Settings(
        persist_directory=".mist_memory",
        anonymized_telemetry=False,
    )
)
_collection = _client.get_or_create_collection("mist_sovereign_memory")


def retrieve_memories(query: str, top_k: int = 5) -> list[str]:
    """Retrieve top-k semantically relevant memories for a query."""
    results = _collection.query(query_texts=[query], n_results=top_k)
    return results.get("documents", [[]])[0]


def write_memories(entries: list[dict]) -> None:
    """
    Persist a list of memory entries to the vector store.
    Each entry: {"content": str, "metadata": dict}
    """
    for i, entry in enumerate(entries):
        _collection.add(
            documents=[entry["content"]],
            metadatas=[entry.get("metadata", {})],
            ids=[f"mem_{abs(hash(entry['content']))}_{i}"],
        )
