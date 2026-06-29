from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    query: str = Field(..., max_length=500, description="User's question")
    session_id: Optional[str] = Field(None, description="Optional session ID")

class ChatResponse(BaseModel):
    answer: str
    source_url: str
    last_updated: str
    intent: str              # FACTUAL, ADVISORY, PII_DETECTED, OUT_OF_SCOPE
    confidence: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    vector_store_docs: int
    last_ingestion: str
