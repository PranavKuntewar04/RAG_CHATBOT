import os
import sys
import logging
from src.ingestion.chunker import chunk_all
from src.ingestion.embedder import embed_texts
from src.retrieval.vector_store import add_documents, collection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting ingestion pipeline...")
    
    # Step 1 & 2: Load and chunk all parsed JSON from data/parsed/
    chunks = chunk_all()
    if not chunks:
        logger.error("No chunks generated. Exiting.")
        return
        
    # Step 3: Embed all chunk texts -> embeddings matrix
    logger.info(f"Generating embeddings for {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    
    # Step 4: Upsert into ChromaDB collection
    logger.info(f"Upserting {len(embeddings)} embeddings to ChromaDB...")
    add_documents(chunks, embeddings)
    
    # Step 5: Print summary
    collection_count = collection.count()
    logger.info("Ingestion complete.")
    logger.info(f"ChromaDB collection size: {collection_count}")

if __name__ == "__main__":
    # Windows console defaults to cp1252 which can't print ₹ — force UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
    main()
