from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.models import ChatRequest, ChatResponse, HealthResponse
from src.guardrails.input_guard import classify_query
from src.guardrails.output_guard import validate_output
from src.retrieval.vector_store import query as vector_query, collection
from src.generation.llm_client import generate
from src.generation.prompt_templates import (
    SYSTEM_PROMPT, REFUSAL_PII, REFUSAL_ADVISORY, 
    REFUSAL_PROMPT_INJECTION, REFUSAL_TOO_LONG
)
from src.ingestion.embedder import embed_query

app = FastAPI(title="Mutual Fund FAQ Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Classify query
    intent = classify_query(request.query)
    
    # 2. If not FACTUAL -> return refusal
    if intent == "PII_DETECTED":
        return ChatResponse(answer=REFUSAL_PII, source_url="", last_updated="", intent=intent)
    elif intent == "ADVISORY":
        return ChatResponse(answer=REFUSAL_ADVISORY, source_url="", last_updated="", intent=intent)
    elif intent == "PROMPT_INJECTION":
        return ChatResponse(answer=REFUSAL_PROMPT_INJECTION, source_url="", last_updated="", intent=intent)
    elif intent == "TOO_LONG":
        return ChatResponse(answer=REFUSAL_TOO_LONG, source_url="", last_updated="", intent=intent)
        
    # 3. Retrieve chunks from ChromaDB
    query_embedding = embed_query(request.query)
    
    # Top K = 5 as per phase 4
    results = vector_query(query_embedding=query_embedding, top_k=5)
    
    if not results or not results.get('documents') or len(results['documents'][0]) == 0:
        return ChatResponse(
            answer="I don't have enough information to answer that based on the provided data.",
            source_url="",
            last_updated="Unknown",
            intent=intent
        )
        
    # Assemble context
    chunks = results['documents'][0]
    metadatas = results['metadatas'][0]
    
    context_parts = []
    for doc, meta in zip(chunks, metadatas):
        context_parts.append(f"Document: {doc}")
    context = "\n\n".join(context_parts)
    
    # Get metadata for the top chunk (most relevant)
    top_meta = metadatas[0] if metadatas else {}
    source_url = top_meta.get("source_url", "")
    scrape_date = top_meta.get("scrape_date", "Unknown")

    # 4. Generate LLM response
    raw_answer = generate(
        system_prompt=SYSTEM_PROMPT,
        user_query=request.query,
        context=context
    )
    
    # 5. Validate output
    validated = validate_output(
        answer=raw_answer,
        source_url=source_url,
        scrape_date=scrape_date
    )
    
    # 6. Return ChatResponse
    return ChatResponse(
        answer=validated["answer"],
        source_url=validated["source_url"],
        last_updated=validated["last_updated"],
        intent=intent
    )

@app.get("/api/health", response_model=HealthResponse)
async def health():
    try:
        count = collection.count()
    except Exception:
        count = 0
    return HealthResponse(
        status="healthy",
        vector_store_docs=count,
        last_ingestion="Unknown"
    )
