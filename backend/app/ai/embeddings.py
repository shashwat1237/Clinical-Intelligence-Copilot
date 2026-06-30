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
                    # FIX: Correctly structured super() call
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
        High-performance batch inference with strict memory limits.
        """
        if not texts:
            return []
        
        # 🚨 CRITICAL FIX 1: Add batch_size=8 to prevent PyTorch from overflowing 512MB RAM
        embeddings = self.model.encode(texts, batch_size=8)
        return embeddings.tolist()

class VectorIndexer:
    def __init__(self, embedding_engine=None):
        self.embedding_engine = embedding_engine or EmbeddingEngine()

    def index_document(self, db: Session, document_id: str, patient_id: str, chunks: List[dict]):
        """Generates localized dense array dimensions and inserts data records safely via pgvector mappings."""
        if not chunks:
            return

        # 🚨 CRITICAL FIX 2 (OOM RESOLUTION): Chunk BOTH the ML Inference AND the DB inserts together.
        # Previously, the system generated vectors for the entire document at once, crashing the 512MB limit.
        # Now, it only embeds and holds 15 chunks in RAM before flushing to the database.
        DB_BATCH_SIZE = 15
        
        for i in range(0, len(chunks), DB_BATCH_SIZE):
            chunk_batch = chunks[i:i + DB_BATCH_SIZE]
            
            # Extract text for just this small batch
            texts = [chunk["content"] for chunk in chunk_batch]
            
            # Fire the constrained Batch Inference strictly for these 15 items
            emb_batch = self.embedding_engine.generate_embeddings_batch(texts)
            
            new_chunks = []
            for chunk, embedding in zip(chunk_batch, emb_batch):
                new_chunks.append(
                    VectorChunk(
                        document_id=document_id,
                        patient_id=patient_id,
                        page=chunk["page"],
                        content=chunk["content"],
                        embedding=embedding
                    )
                )
            
            if new_chunks:
                db.add_all(new_chunks)
                db.commit() # Flush transaction and free memory

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
