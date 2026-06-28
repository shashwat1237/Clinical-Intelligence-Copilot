from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Document
from app.services.extraction import process_document_workflow

router = APIRouter()

@router.post("/documents/{document_id}/retry")
async def retry_extraction(
    document_id: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Failsafe endpoint to retry documents stuck in EXTRACTING state."""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if document.status == "READY":
        raise HTTPException(status_code=400, detail="Document is already processed")
        
    # Reset status to QUEUED and re-trigger background task
    document.status = "QUEUED"
    db.commit()
    
    background_tasks.add_task(process_document_workflow, document.id, db)
    
    return {"message": "Extraction workflow re-triggered successfully", "status": "QUEUED"}
