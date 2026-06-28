from sqlalchemy.orm import Session
from app.db import models_and_crud
from app.ai.embeddings import VectorIndexer

class SearchService:
    def __init__(self, db: Session, patient_id: str):
        self.db = db
        self.patient_id = patient_id
        self.indexer = VectorIndexer()

    def hybrid_search(self, query: str):
        """Combines SQL filtering with pgvector search."""
        # 1. Semantic Retrieval (Passed DB context)
        vector_results = self.indexer.search(self.db, query, self.patient_id, top_k=3)
        
        # 2. Structured Lookup 
        sql_entities = self.db.query(models_and_crud.ClinicalEntity).filter(
            models_and_crud.ClinicalEntity.patient_id == self.patient_id,
            models_and_crud.ClinicalEntity.normalized_name.ilike(f"%{query}%")
        ).all()

        return {
            "semantic_evidence": vector_results,
            "structured_matches": [{"id": e.id, "name": e.normalized_name} for e in sql_entities]
        }

