from sentence_transformers import SentenceTransformer

# BGE-small-en-v1.5: 384-dim, 33M params, ~130 MB
# Ideal for our small corpus of 168 short chunks (avg 32 tokens)
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# BGE models use a query instruction prefix for asymmetric retrieval
# This prefix is prepended to QUERIES only, not to document chunks
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed document chunks (no instruction prefix)."""
    return model.encode(texts, show_progress_bar=True, normalize_embeddings=True).tolist()


def embed_query(query: str) -> list[float]:
    """Embed a user query with the BGE instruction prefix for better retrieval."""
    prefixed = QUERY_INSTRUCTION + query
    return model.encode(prefixed, normalize_embeddings=True).tolist()
