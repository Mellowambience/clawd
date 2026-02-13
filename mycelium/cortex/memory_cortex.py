import chromadb
from chromadb.config import Settings
import os
from datetime import datetime
import hashlib

class MemoryCortex:
    def __init__(self, db_path="chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="rin_memory")
        print(f"Memory Cortex Initialized at {db_path}")

    def ingest_text(self, text, metadata=None):
        if not text.strip():
            return
        
        # Debounce/Filter: Ignore the redundant heartbeat messages
        if "sister heartbeat sent" in text.lower():
            return

        doc_id = hashlib.md5(text.encode()).hexdigest()
        
        if metadata is None:
            metadata = {"timestamp": datetime.now().isoformat()}
            
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query_memory(self, query_text, n_results=5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

    def list_recent_memories(self, limit=10):
        # Retrieve the most recent entries
        return self.collection.get(limit=limit)

if __name__ == "__main__":
    # Test
    cortex = MemoryCortex()
    cortex.ingest_text("Establish connection... Source Link Active.")
    results = cortex.query_memory("connection")
    print("Test Results:", results)
