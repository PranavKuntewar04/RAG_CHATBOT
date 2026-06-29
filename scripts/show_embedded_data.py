import sys
from src.retrieval.vector_store import collection

def main():
    total = collection.count()
    print(f"Total items in ChromaDB: {total}")
    
    if total == 0:
        print("No embedded data found in ChromaDB.")
        return
        
    # Retrieve a few items including their embeddings, text documents, and metadata
    results = collection.get(
        include=["embeddings", "documents", "metadatas"],
        limit=3
    )
    
    print("\n" + "="*60)
    print("SAMPLE OF EMBEDDED DATA (First 3 chunks)")
    print("="*60)
    
    for i in range(len(results["ids"])):
        print(f"\n[ID]: {results['ids'][i]}")
        print(f"[Text Document]: {results['documents'][i][:120]}...")
        
        # Display metadata
        meta = results['metadatas'][i]
        meta_preview = {k: meta[k] for k in meta if k != 'source_url'}
        print(f"[Metadata]: {meta_preview}")
        
        # The embedding is a list of 384 floats. We'll show the first 5 to give you an idea.
        embedding = results['embeddings'][i]
        sliced_emb = ", ".join([f"{x:.4f}" for x in embedding[:5]])
        print(f"[Embedding Vector]: [{sliced_emb}, ...] (Total Dimensions: {len(embedding)})")
        print("-" * 60)

if __name__ == "__main__":
    # Force UTF-8 encoding for Windows terminals (helps to print the rupee ₹ symbol)
    sys.stdout.reconfigure(encoding="utf-8")
    main()
