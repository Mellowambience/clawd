# gateway/memory.py
"""MIST Memory Layer - Chroma-backed sovereign vector store."""
import chromadb
from chromadb.config import Settings

_client = chromadb.Client(Settings(persist_directory=".mist_memory", anonymized_telemetry=False))
_collection = _client.get_or_create_collection("mist_sovereign_memory")


def retrieve_memories(query: str, top_k: int = 5) -> list:
    results = _collection.query(query_texts=[query], n_results=top_k)
    return results.get("documents", [[]])[0]


def write_memories(entries: list) -> None:
    for i, entry in enumerate(entries):
        _collection.add(
            documents=[entry["content"]],
            metadatas=[entry.get("metadata", {})],
            ids=[f"mem_{abs(hash(entry['content']))}_{i}"],
        )


def export_memories(output_path: str = "mist_memory_export.json") -> None:
    import json as _json
    result = _collection.get()
    with open(output_path, "w", encoding="utf-8") as f:
        _json.dump(result, f, indent=2, default=str)
    print(f"Memory exported to {output_path} ({len(result.get('ids', []))} entries)")
