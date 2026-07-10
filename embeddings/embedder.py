import os
import sys
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer

# Add parent directory to path so config can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import EMBEDDING_MODEL

class DocumentEmbedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
    def embed_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 32) -> List[Tuple[str, List[float], Dict[str, Any]]]:
        """
        Takes a list of chunk dictionaries (with 'text' and 'metadata')
        and returns a list of tuples: (chunk_text, embedding_vector, metadata)
        """
        texts = [chunk["text"] for chunk in chunks]
        
        print(f"Encoding {len(texts)} chunks in batches of {batch_size}...")
        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=True)
        
        result = []
        for i, chunk in enumerate(chunks):
            embedding_vector = embeddings[i].tolist()
            result.append((chunk["text"], embedding_vector, chunk.get("metadata", {})))
            
        return result

    def embed_query(self, query: str) -> List[float]:
        """
        Embeds a single search query.
        """
        return self.model.encode(query).tolist()

if __name__ == "__main__":
    import json
    
    # Simple test run on saved chunks
    embedder = DocumentEmbedder()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chunks_file = os.path.join(base_dir, "data", "chunks", "all_chunks.json")
    
    if os.path.exists(chunks_file):
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        print(f"Loaded {len(chunks)} chunks from {chunks_file}")
        # Test with just a small subset so we don't wait too long
        test_chunks = chunks[:5]
        embedded_data = embedder.embed_chunks(test_chunks)
        
        print(f"Successfully embedded {len(embedded_data)} chunks.")
        print(f"Embedding vector dimension: {len(embedded_data[0][1])}")
    else:
        print(f"No chunks file found at {chunks_file}. Run chunker.py first.")
