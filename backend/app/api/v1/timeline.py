from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_user
from app.db.session import get_db
from app.db import models_and_crud
from app.schemas.patient_and_timeline import TimelineEventSchema

router = APIRouter()

@router.get("/", response_model=List[TimelineEventSchema])
def get_timeline(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Timeline generation occurs during ingestion; this just retrieves it deterministically."""
    patient = models_and_crud.get_patient_by_user(db, user_id)
    events = models_and_crud.get_timeline_for_patient(db, patient.id)
    return events

