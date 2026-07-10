import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.retriever import Retriever

@pytest.fixture
def mock_retriever():
    with patch('pipeline.retriever.DocumentEmbedder') as MockEmbedder, \
         patch('pipeline.retriever.VectorStore') as MockVectorStore:
        
        # Setup mocks
        mock_embedder_instance = MockEmbedder.return_value
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        
        mock_vs_instance = MockVectorStore.return_value
        mock_vs_instance.search.return_value = [
            {"chunk_id": "test-1", "similarity": 0.9, "text": "HDFC Large Cap Fund...", "metadata": {"source_url": "http://groww.in/test1"}},
            {"chunk_id": "test-2", "similarity": 0.8, "text": "More info...", "metadata": {"source_url": "http://groww.in/test1"}}
        ]
        
        retriever = Retriever()
        retriever.embedder = mock_embedder_instance
        retriever.vector_store = mock_vs_instance
        yield retriever

def test_retriever_returns_results(mock_retriever):
    results = mock_retriever.retrieve("What is HDFC Large Cap?")
    
    assert len(results) == 2
    assert results[0]["chunk_id"] == "test-1"
    assert results[0]["similarity"] == 0.9
    
    # Check if embedder was called correctly
    mock_retriever.embedder.embed_query.assert_called_once_with("What is HDFC Large Cap?")
    
    # Check if vector store search was called correctly
    mock_retriever.vector_store.search.assert_called_once()
