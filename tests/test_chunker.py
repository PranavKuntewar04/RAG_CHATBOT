import pytest
from src.ingestion.chunker import chunk_document

def test_chunk_document():
    parsed_doc = {
        "scheme_name": "Test Fund",
        "source_url": "http://test.com",
        "category": "Equity",
        "scrape_date": "2026-06-29",
        "sections": [
            {
                "heading": "Fund Overview",
                "content": "This is a test fund."
            },
            {
                "heading": "Fund Details",
                "content": "Expense Ratio: 1.0%"
            }
        ],
        "structured_data": {
            "nav": "100.0",
            "expense_ratio": "1.0%",
            "exit_load": "1%"
        }
    }
    
    chunks = chunk_document(parsed_doc)
    
    # 3 attributes + 2 sections + 1 full doc = 6 chunks
    assert len(chunks) == 6
    
    # Check attribute chunks
    attr_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "attribute"]
    assert len(attr_chunks) == 3
    assert any("The NAV (Net Asset Value) of Test Fund is ₹100.0." in c["text"] for c in attr_chunks)
    assert any(c["metadata"]["attribute"] == "nav" for c in attr_chunks)
    
    # Check section chunks
    sec_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "section"]
    assert len(sec_chunks) == 2
    assert sec_chunks[0]["text"] == "This is a test fund."
    
    # Check full doc chunk
    full_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "full_document"]
    assert len(full_chunks) == 1
    assert full_chunks[0]["text"] == "This is a test fund. Expense Ratio: 1.0%"
    
    # Check base metadata
    for chunk in chunks:
        assert chunk["metadata"]["scheme_name"] == "Test Fund"
        assert chunk["metadata"]["source_url"] == "http://test.com"
        assert chunk["metadata"]["category"] == "Equity"
