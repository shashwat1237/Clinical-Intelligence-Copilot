from app.ai.embeddings import VectorIndexer
import os

def test_vector_indexer(mocker):
    mock_db = mocker.MagicMock()
    indexer = VectorIndexer()
    
    # Bypass actual DB insertion
    mocker.patch.object(mock_db, "add")
    mocker.patch.object(mock_db, "commit")
    
    test_chunks = [{"page": 1, "content": "Patient shows signs of diabetes."}]
    indexer.index_document(mock_db, "doc_1", "pat_1", test_chunks)
    
    assert mock_db.add.called

