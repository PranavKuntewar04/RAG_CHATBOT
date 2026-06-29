import sys
from src.retrieval.vector_store import collection, query
from src.ingestion.embedder import embed_query

def main():
    print(f"Total chunks in ChromaDB: {collection.count()}")

    print("\n--- Test 1: Expense ratio query ---")
    q1 = "What is the expense ratio of HDFC Mid Cap Fund?"
    q1_emb = embed_query(q1)
    res1 = query(q1_emb, top_k=1)
    print("Top result metadata:", res1["metadatas"][0][0])
    print("Top result text:", res1["documents"][0][0])

    print("\n--- Test 2: Broad query ---")
    q2 = "Tell me about HDFC Defence Fund"
    q2_emb = embed_query(q2)
    res2 = query(q2_emb, top_k=1)
    print("Top result metadata:", res2["metadatas"][0][0])
    print("Top result text:", res2["documents"][0][0][:150] + "...")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
