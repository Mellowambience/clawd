import chromadb
import os
import datetime

class MemoryVault:
    """
    AetherClaw Persistent Memory Layer.
    Uses ChromaDB for vector retrieval.
    """
    def __init__(self):
        self.db_path = "c:/Users/nator/clawd/aether_pod/data/chroma"
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)
            
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(name="shadow_memory")

    def store(self, query, response):
        timestamp = datetime.datetime.now().isoformat()
        doc_id = f"mem_{datetime.datetime.now().timestamp()}"
        self.collection.add(
            documents=[f"Q: {query}\nA: {response}"],
            metadatas=[{"timestamp": timestamp, "type": "chat"}],
            ids=[doc_id]
        )

    def retrieve(self, query, n_results=5):
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return "\n---\n".join(results['documents'][0]) if results['documents'] else ""
        except:
            return ""

    def ingest_logs(self, log_dir="c:/Users/nator/clawd/aether_pod/data/logs"):
        """Ingests raw text logs into the vector vault."""
        if not os.path.exists(log_dir): return
        for f in os.listdir(log_dir):
            if f.endswith(".md") or f.endswith(".log"):
                with open(os.path.join(log_dir, f), "r", encoding="utf-8") as file:
                    content = file.read()
                    self.collection.add(
                        documents=[content],
                        metadatas=[{"source": f, "ingested": datetime.datetime.now().isoformat()}],
                        ids=[f"log_{f}_{datetime.datetime.now().timestamp()}"]
                    )
