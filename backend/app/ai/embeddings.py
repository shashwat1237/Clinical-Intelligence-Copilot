import threading
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any

from app.db.models_and_crud import VectorChunk 
from app.core.config import logger

class EmbeddingEngine:
    """Singleton implementation pattern protecting memory buffers from out-of-memory runtime system deaths."""
    _instance = None
    _model = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmbeddingEngine, cls).__new__(cls)
        return cls._instance

    @property
    def model(self):
        # Lazy load the model ONLY when a vector operation is explicitly requested
        if self._model is None:
            with self._lock:
                if self._model is None:
                    logger.info("Lazy Loading: Importing heavy ML libraries and bootstrapping weights...")
                    
                    # 🚨 CRITICAL FIX: LAZY IMPORT 🚨
                    from sentence_transformers import SentenceTransformer
                    
                    self._model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._model

    def generate_embedding(self, text: str) -> List[float]:
        """Legacy single-string embedding method."""
        if not text or not text.strip():
            return [0.0] * 384
        return self.model.encode(text).tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        High-performance batch inference. 
        Processes all chunks in a single PyTorch matrix operation instead of sequentially.
        """
        if not texts:
            return []
        
        # SentenceTransformer natively accepts lists of strings for optimized batching
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

class VectorIndexer:
    def __init__(self, embedding_engine=None):
        self.embedding_engine = embedding_engine or EmbeddingEngine()

    def index_document(self, db: Session, document_id: str, patient_id: str, chunks: List[dict]):
        """Generates localized dense array dimensions and inserts data records safely via pgvector mappings."""
        if not chunks:
            return

        # 1. Extract all text content into a single list
        texts = [chunk["content"] for chunk in chunks]
        
        # 2. Fire the Batch Inference (Massive CPU speedup)
        vector_embeddings = self.embedding_engine.generate_embeddings_batch(texts)
        
        # 3. Map embeddings back to their metadata
        new_chunks = []
        for chunk, embedding in zip(chunks, vector_embeddings):
            new_chunks.append(
                VectorChunk(
                    document_id=document_id,
                    patient_id=patient_id,
                    page=chunk["page"],
                    content=chunk["content"],
                    embedding=embedding
                )
            )
        
        # 4. Bulk insert into Postgres instead of hitting the DB iteratively
        if new_chunks:
            db.add_all(new_chunks)
            db.commit()

    def search(self, db: Session, query: str, patient_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Executes a strict cosine distance vector evaluation search scoped cleanly behind active patient boundaries."""
        query_embedding = self.embedding_engine.generate_embedding(query)
        
        stmt = (
            select(VectorChunk)
            .filter(VectorChunk.patient_id == patient_id)
            .order_by(VectorChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        
        results = db.execute(stmt).scalars().all()
        return [{"doc_id": res.document_id, "page": res.page, "excerpt": res.content} for res in results]
