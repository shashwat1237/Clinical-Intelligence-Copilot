from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db import models_and_crud
from app.ai.embeddings import VectorIndexer

class Router:
    """Agent Layer: Gathers the necessary evidence to answer the user's query."""
    def __init__(self, db: Session, patient_id: str):
        self.db = db
        self.patient_id = patient_id
        self.indexer = VectorIndexer()

    def assemble_context(self, user_question: str, plan: dict) -> str:
        # Use chr(10) to generate newlines so editors cannot strip backslashes
        NL = chr(10)
        NL2 = chr(10) + chr(10)
        
        evidence_text = []
        citation_index = 1
        
        # Pre-fetch document names
        docs = {d.id: d.filename for d in models_and_crud.get_documents_by_patient(self.db, self.patient_id)}
        
        strategy = plan.get("strategy", "HYBRID")
        entities_to_search = plan.get("entities_to_search", [])
        
        # 1. Fetch Structured Data (Algorithmic Honesty: Respecting Planner Strategy)
        if strategy in ["SQL_ONLY", "HYBRID"]:
            query = self.db.query(models_and_crud.ClinicalEntity).filter(
                models_and_crud.ClinicalEntity.patient_id == self.patient_id
            )
            
            # Apply Planner's filtering if specific entities were identified to prevent context explosion
            if entities_to_search:
                filters = [models_and_crud.ClinicalEntity.normalized_name.ilike(f"%{term}%") for term in entities_to_search]
                query = query.filter(or_(*filters))
                
            entities = query.limit(50).all() 
            
            for e in entities:
                doc_name = docs.get(e.document_id, "Unknown Report")
                evidence_text.append(
                    f"[{citation_index}] Source: {doc_name} (Page 1){NL}Excerpt: Structured Record - {e.category}: {e.normalized_name} ({e.value})"
                )
                citation_index += 1
            
        # 2. Fetch Semantic Chunks
        if strategy in ["HYBRID", "VECTOR_ONLY"]:
            # Always retrieve top_k=6 for deep context
            vector_results = self.indexer.search(self.db, user_question, self.patient_id, top_k=6)
            if vector_results:
                for res in vector_results:
                    doc_name = docs.get(res['doc_id'], "Unknown Report")
                    evidence_text.append(
                        f"[{citation_index}] Source: {doc_name} (Page {res['page']}){NL}Excerpt: {res['excerpt']}"
                    )
                    citation_index += 1

        if not evidence_text:
            return "No clinical records found for this patient."

        return f"### Clinical Evidence ###{NL}" + NL2.join(evidence_text)