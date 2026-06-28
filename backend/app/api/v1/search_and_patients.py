from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.db import models_and_crud
from app.schemas.patient_and_timeline import PatientProfileSchema
from app.services.search import SearchService

router = APIRouter()

@router.get("/profile", response_model=PatientProfileSchema)
def get_patient_profile(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = models_and_crud.get_patient_by_user(db, user_id)
    conditions = models_and_crud.get_entities_by_category(db, patient.id, "Condition")
    medications = models_and_crud.get_entities_by_category(db, patient.id, "Medication")
    labs = models_and_crud.get_entities_by_category(db, patient.id, "LabResult")
    
    # Format according to Schema
    return {
        "conditions": [{"id": c.id, "name": c.normalized_name} for c in conditions],
        "medications": [
            {"id": m.id, "name": m.normalized_name, "dosage": m.value, "frequency": m.metadata_json.get("frequency", "")} 
            for m in medications
        ],
        "labs": [
            {
                "id": l.id, "parameter": l.normalized_name, "value": l.value, 
                "unit": l.metadata_json.get("unit", ""), 
                "is_abnormal": l.metadata_json.get("is_abnormal", False)
            } 
            for l in labs
        ]
    }

@router.get("/search")
def search_clinical_records(q: str, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Hybrid search combining structured DB data and semantic vector retrieval."""
    patient = models_and_crud.get_patient_by_user(db, user_id)
    search_service = SearchService(db, patient.id)
    return search_service.hybrid_search(q)

