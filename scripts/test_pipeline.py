import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.guardrails.input_guard import classify_query
from src.ingestion.embedder import embed_query
from src.retrieval.vector_store import query as vector_query
from src.generation.llm_client import generate
from src.generation.prompt_templates import SYSTEM_PROMPT, REFUSAL_PII, REFUSAL_ADVISORY
from src.generation.response_builder import build_response

def run_pipeline(user_query: str):
    print(f"\n--- Processing Query: '{user_query}' ---")
    
    # 1. Classify intent
    intent = classify_query(user_query)
    print(f"1. Intent Classification: {intent}")
    
    if intent == "PII_DETECTED":
        print(f"-> Response: {REFUSAL_PII}")
        return
    elif intent == "ADVISORY":
        print(f"-> Response: {REFUSAL_ADVISORY}")
        return
        
    # 2. Embed & Retrieve
    query_emb = embed_query(user_query)
    # Using top_k=5
    results = vector_query(query_embedding=query_emb, top_k=5)
    
    if not results or not results["documents"] or not results["documents"][0]:
        print("2. Retrieval: No chunks found.")
        return
        
    top_chunks = results["documents"][0]
    top_metadatas = results["metadatas"][0]
    
    print(f"2. Retrieval: Found {len(top_chunks)} chunks.")
    for i, (chunk, meta) in enumerate(zip(top_chunks, top_metadatas)):
        print(f"   Chunk {i+1} [{meta.get('chunk_type', 'unknown')}]: {chunk[:50]}...")
    
    # Assemble context
    # Add source URLs to context
    context_parts = []
    for chunk, meta in zip(top_chunks, top_metadatas):
        source = meta.get("source_url", "unknown source")
        context_parts.append(f"[Source: {source}]\n{chunk}")
        
    context_str = "\n\n".join(context_parts)
    
    # Generate response
    print("3. Generating LLM Response...")
    raw_response = generate(
        system_prompt=SYSTEM_PROMPT,
        user_query=user_query,
        context=context_str
    )
    
    # Build final response (using first chunk's metadata for citation)
    primary_source = top_metadatas[0].get("source_url", "No source")
    primary_date = top_metadatas[0].get("scrape_date", "Unknown date")
    
    final_response = build_response(raw_response, primary_source, primary_date)
    
    print("\n--- Final Response ---")
    print(final_response["answer"])
    print(f"\nSource: {final_response['source_url']}")
    print(f"Last updated: {final_response['last_updated']}")

if __name__ == "__main__":
    test_queries = [
        "What is the expense ratio of HDFC Mid Cap Fund?",
        "Should I invest in HDFC Mid Cap Fund?",
        "My PAN is ABCDE1234F, tell me about HDFC equity fund.",
        "What is the minimum SIP amount for HDFC Large Cap Fund?"
    ]
    
    for q in test_queries:
        run_pipeline(q)
