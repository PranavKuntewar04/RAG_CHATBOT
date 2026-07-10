import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from embeddings.embedder import DocumentEmbedder

def test_embed_chunks():
    embedder = DocumentEmbedder(model_name="BAAI/bge-small-en-v1.5")
    
    mock_chunks = [
        {"text": "This is a test chunk.", "metadata": {"chunk_id": "test-001"}},
        {"text": "This is another test chunk with different text.", "metadata": {"chunk_id": "test-002"}},
    ]
    
    result = embedder.embed_chunks(mock_chunks)
    
    assert len(result) == 2
    assert len(result[0]) == 3 # text, embedding, metadata
    
    # Check text
    assert result[0][0] == "This is a test chunk."
    assert result[1][0] == "This is another test chunk with different text."
    
    # Check embeddings (BGE-small is 384 dimensions)
    assert len(result[0][1]) == 384
    assert len(result[1][1]) == 384
    
    # Check metadata
    assert result[0][2]["chunk_id"] == "test-001"
    assert result[1][2]["chunk_id"] == "test-002"
