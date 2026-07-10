import os
import sys
import json
import numpy as np

# Add parent directory to path so config can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from embeddings.embedder import DocumentEmbedder
from embeddings.vector_store import VectorStore

def verify_embeddings():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chunks_file = os.path.join(base_dir, "data", "chunks", "all_chunks.json")
    
    if not os.path.exists(chunks_file):
        print(f"Chunks file not found at {chunks_file}. Please run chunker.py first to generate the chunks.")
        return
        
    print(f"Loading chunks from {chunks_file}...")
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    print(f"Total chunks loaded: {len(chunks)}")
    
    embedder = DocumentEmbedder()
    print("\nGenerating embeddings for all chunks...")
    embedded_data = embedder.embed_chunks(chunks)
    
    print("\n--- Verifying Embeddings ---")
    all_lengths_correct = True
    expected_dim = 384 # BGE-small-en-v1.5 output dimension
    
    for i, (text, emb, meta) in enumerate(embedded_data):
        if len(emb) != expected_dim:
            all_lengths_correct = False
            print(f"ERROR: Chunk {meta.get('chunk_id')} has dimension {len(emb)}")
    
    if all_lengths_correct:
        print(f"SUCCESS: All {len(embedded_data)} chunks have the correct embedding dimension ({expected_dim}).")
        
    # Check for NaN values
    has_nan = any(np.isnan(emb).any() for _, emb, _ in embedded_data)
    if has_nan:
        print("ERROR: Some embeddings contain NaN values.")
    else:
        print("SUCCESS: No NaN values found in embeddings.")
        
    print("\n--- Vector Store Verification ---")
    vs = VectorStore()
    vs.upsert_chunks(embedded_data)
    
    # Verify chroma collection count
    collection_count = vs.collection.count()
    print(f"\nTotal items successfully stored in ChromaDB collection '{vs.collection.name}': {collection_count}")
    
    if collection_count >= len(chunks):
        print("SUCCESS: All chunks are present in the Vector Store.")
    else:
        print(f"WARNING: ChromaDB count ({collection_count}) is less than the chunk count ({len(chunks)}).")
        
    # Test a sample chunk query to ensure embeddings are searchable
    if len(embedded_data) > 0:
        sample_query = "What is the expense ratio?"
        print(f"\n--- Testing Query ---")
        print(f"Query: '{sample_query}'")
        q_emb = embedder.embed_query(sample_query)
        results = vs.search(q_emb, top_k=2)
        
        for idx, res in enumerate(results, 1):
            print(f"Result {idx} [Sim: {res['similarity']:.4f}] {res['chunk_id']}: {res['text'][:100].replace('\n', ' ')}...")

if __name__ == "__main__":
    verify_embeddings()
