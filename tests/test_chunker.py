import os
import sys
import pytest

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from embeddings.chunker import DocumentChunker

def test_chunk_document():
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    
    mock_data = {
        "metadata": {
            "source_url": "https://example.com/fund",
            "scheme_name": "Test Fund",
            "scrape_date": "2026-07-10"
        },
        "fund_details": {
            "NAV": "100.5"
        },
        "text": "This is a very long text that should be split into multiple chunks because it exceeds the chunk size of one hundred characters. We will see how it works."
    }
    
    chunks = chunker.chunk_document(mock_data)
    
    assert len(chunks) > 1, "Document should be split into multiple chunks"
    
    first_chunk = chunks[0]
    assert "metadata" in first_chunk
    assert "chunk_id" in first_chunk["metadata"]
    assert first_chunk["metadata"]["scheme_name"] == "Test Fund"
    
    # Check that fund_details were prepended
    assert "Fund Details:" in first_chunk["text"]
    assert "NAV: 100.5" in first_chunk["text"]

def test_chunk_all_documents(tmp_path):
    import json
    
    # Create temporary mock json files
    mock_data_1 = {
        "metadata": {"scheme_name": "Fund A"},
        "text": "Text for fund A"
    }
    mock_data_2 = {
        "metadata": {"scheme_name": "Fund B"},
        "text": "Text for fund B"
    }
    
    file_1 = tmp_path / "fund_a.json"
    file_1.write_text(json.dumps(mock_data_1))
    
    file_2 = tmp_path / "fund_b.json"
    file_2.write_text(json.dumps(mock_data_2))
    
    chunker = DocumentChunker()
    chunks = chunker.chunk_all_documents(str(tmp_path))
    
    assert len(chunks) == 2
    chunk_ids = [c["chunk_id"] for c in chunks]
    assert "fund-a-000" in chunk_ids
    assert "fund-b-000" in chunk_ids
