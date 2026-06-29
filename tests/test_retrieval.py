import pytest
from unittest.mock import patch, MagicMock
from src.retrieval import vector_store

@patch("src.retrieval.vector_store.collection")
def test_add_documents(mock_collection):
    chunks = [
        {"text": "Test 1", "metadata": {"chunk_type": "section"}},
        {"text": "Test 2", "metadata": {"chunk_type": "attribute"}}
    ]
    embeddings = [[0.1, 0.2], [0.3, 0.4]]
    
    vector_store.add_documents(chunks, embeddings)
    
    mock_collection.add.assert_called_once_with(
        ids=["chunk_0", "chunk_1"],
        documents=["Test 1", "Test 2"],
        metadatas=[{"chunk_type": "section"}, {"chunk_type": "attribute"}],
        embeddings=[[0.1, 0.2], [0.3, 0.4]]
    )

@patch("src.retrieval.vector_store.collection")
def test_query(mock_collection):
    mock_collection.query.return_value = {
        "ids": [["chunk_0"]],
        "documents": [["Test 1"]],
        "metadatas": [[{"chunk_type": "section"}]],
        "distances": [[0.5]]
    }
    
    query_emb = [0.1, 0.2]
    res = vector_store.query(query_emb, top_k=1, filters={"scheme_name": "Test"})
    
    mock_collection.query.assert_called_once_with(
        query_embeddings=[[0.1, 0.2]],
        n_results=1,
        where={"scheme_name": "Test"}
    )
    
    assert res["documents"][0][0] == "Test 1"
