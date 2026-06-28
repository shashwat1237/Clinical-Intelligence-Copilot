import uuid
import urllib.parse
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.db import models_and_crud
from app.services import storage, extraction
from app.schemas.document import DocumentResponse
from app.core.config import logger

router = APIRouter()

@router.post("/", response_model=DocumentResponse, status_code=202)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Unsupported format: Only text-based PDFs are processed.")
    
    # ==========================================
    # DATABASE AUTO-HEALING & PROVISIONING
    # ==========================================
    patient = models_and_crud.get_patient_by_user(db, user_id)
    
    if not patient:
        logger.warning(f"Patient profile missing for {user_id}. Auto-provisioning database records now...")
        try:
            # 1. Ensure the base User row exists
            db_user = db.query(models_and_crud.User).filter(models_and_crud.User.id == user_id).first()
            if not db_user:
                models_and_crud.create_user(db, user_id=user_id, email=f"{user_id}@auto-provisioned.local")
            
            # 2. Create the linked Patient profile
            patient = models_and_crud.create_patient_profile(db, user_id=user_id)
            logger.info("Auto-provisioning successful. User is fully synced with PostgreSQL.")
        except Exception as e:
            logger.error(f"Database sync failure: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize user database profile.")
    # ==========================================

    file_bytes = file.file.read()
    
    # FIX: Generate a unique and URL-safe storage path to prevent overwrite conflicts and iframe encoding bugs
    safe_filename = urllib.parse.quote(file.filename.replace(" ", "_"))
    unique_file_id = str(uuid.uuid4())[:8]
    storage_filename = f"{unique_file_id}_{safe_filename}"
    
    # Delegate persistence directly to storage engine
    storage_path = storage.upload_pdf(file_bytes, storage_filename, user_id)
    
    # Initialize the document in a canonical QUEUED processing state (Keep original filename for UI display)
    document = models_and_crud.create_document(db, patient.id, file.filename, storage_path)
    
    logger.info(f"Ingestion Pipeline: Document {document.id} registered and queued.")
    
    # Handoff background threads smoothly to prevent HTTP blocking timeouts
    background_tasks.add_task(
        extraction.process_document_workflow, 
        document.id, 
        storage_path, 
        patient.id, 
        user_id
    )
    
    return document