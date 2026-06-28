from sqlalchemy.orm import Session
from app.db import models_and_crud

class TimelineService:
    def __init__(self, db: Session, patient_id: str):
        self.db = db
        self.patient_id = patient_id

    def get_chronological_history(self):
        """Fetches pre-computed events directly from Postgres."""
        return models_and_crud.get_timeline_for_patient(self.db, self.patient_id)

