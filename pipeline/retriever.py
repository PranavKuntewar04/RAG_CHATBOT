import os
import sys
from typing import List, Dict, Any, Tuple, Optional

# Add parent directory to path so modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import TOP_K, SIMILARITY_THRESHOLD
from embeddings.embedder import DocumentEmbedder
from embeddings.vector_store import VectorStore

class Retriever:
    def __init__(self):
        self.embedder = DocumentEmbedder()
        self.vector_store = VectorStore()

    def retrieve(self, query: str, top_k: int = TOP_K, threshold: float = SIMILARITY_THRESHOLD) -> List[Dict[str, Any]]:
        """
        1. Embed user query
        2. Search ChromaDB (top_k, cosine similarity)
        3. Filter by similarity threshold
        4. Return chunks + metadata
        """
        query_embedding = self.embedder.embed_query(query)
        results = self.vector_store.search(query_embedding, top_k=top_k, threshold=threshold)
        return results

if __name__ == "__main__":
    retriever = Retriever()
    res = retriever.retrieve("What is the exit load for HDFC Small Cap Fund?")
    print(f"Found {len(res)} results.")
    for r in res:
        print(f"[{r['similarity']:.4f}] {r['chunk_id']}")
