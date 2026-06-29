import chromadb
from src.config import settings

client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
collection = client.get_or_create_collection(
    name=settings.CHROMA_COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

def add_documents(chunks: list[dict], embeddings: list[list[float]]):
    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
        embeddings=embeddings,
    )

def query(query_embedding: list[float], top_k: int = 5, filters: dict = None):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=filters,
    )
