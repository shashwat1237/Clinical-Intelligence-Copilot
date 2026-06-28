from app.services.search import SearchService

def test_hybrid_search(mocker):
    mock_db = mocker.MagicMock()
    mocker.patch("app.ai.embeddings.VectorIndexer.search", return_value=[])
    
    service = SearchService(mock_db, "pat_1")
    res = service.hybrid_search("Hypertension")
    assert "semantic_evidence" in res
    assert "structured_matches" in res

