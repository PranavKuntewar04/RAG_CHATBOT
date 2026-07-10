import os
import sys
import chromadb
from typing import List, Dict, Any, Tuple

# Add parent directory to path so config can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, TOP_K, SIMILARITY_THRESHOLD

class VectorStore:
    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR, collection_name: str = CHROMA_COLLECTION_NAME):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Resolve persist_dir to an absolute path if it isn't already
        if not os.path.isabs(persist_dir):
            persist_dir = os.path.join(base_dir, persist_dir.replace("./", ""))
            
        os.makedirs(persist_dir, exist_ok=True)
        print(f"Initializing ChromaDB at {persist_dir}")
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # We explicitly use cosine similarity for embedding space
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def upsert_chunks(self, embedded_chunks: List[Tuple[str, List[float], Dict[str, Any]]]):
        """
        Insert or update chunks into the ChromaDB collection.
        embedded_chunks: List of (chunk_text, embedding_vector, metadata) tuples.
        """
        if not embedded_chunks:
            print("No chunks to upsert.")
            return

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for text, embedding, metadata in embedded_chunks:
            # We assume chunk_id is in metadata
            chunk_id = metadata.get("chunk_id")
            if not chunk_id:
                raise ValueError("chunk_id is missing from metadata.")
                
            ids.append(chunk_id)
            documents.append(text)
            embeddings.append(embedding)
            metadatas.append(metadata)

        print(f"Upserting {len(ids)} chunks to collection '{self.collection.name}'...")
        
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        print("Upsert complete.")

    def search(self, query_embedding: List[float], top_k: int = TOP_K, threshold: float = SIMILARITY_THRESHOLD) -> List[Dict[str, Any]]:
        """
        Search for top_k most similar chunks.
        Filters out results with similarity below the threshold.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        filtered_results = []
        if not results["ids"] or not results["ids"][0]:
            return filtered_results

        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            # ChromaDB uses cosine distance = 1 - cosine similarity
            similarity = 1.0 - distance

            if similarity >= threshold:
                filtered_results.append({
                    "chunk_id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": similarity
                })

        return filtered_results

if __name__ == "__main__":
    import json
    from embedder import DocumentEmbedder
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chunks_file = os.path.join(base_dir, "data", "chunks", "all_chunks.json")
    
    if os.path.exists(chunks_file):
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        print(f"Loaded {len(chunks)} chunks.")
        
        # Initialize Embedder and Vector Store
        embedder = DocumentEmbedder()
        vs = VectorStore()
        
        # Embed and upsert
        embedded_data = embedder.embed_chunks(chunks)
        vs.upsert_chunks(embedded_data)
        
        # Test a query
        test_query = "What is the exit load for HDFC Small Cap Fund?"
        print(f"\nTesting Query: '{test_query}'")
        q_emb = embedder.embed_query(test_query)
        results = vs.search(q_emb)
        
        print(f"Found {len(results)} results:")
        for res in results:
            print(f"- [Sim: {res['similarity']:.4f}] {res['chunk_id']}: {res['text'][:100]}...")
            
    else:
        print(f"No chunks file found at {chunks_file}. Run chunker.py first.")
