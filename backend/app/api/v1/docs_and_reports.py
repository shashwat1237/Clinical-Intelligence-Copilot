from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_user
from app.db.session import get_db
from app.db import models_and_crud
from app.schemas.document import DocumentResponse

router = APIRouter()

@router.get("", response_model=List[DocumentResponse])
def list_documents(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = models_and_crud.get_patient_by_user(db, user_id)
    return models_and_crud.get_documents_by_patient(db, patient.id)

@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = models_and_crud.get_document_secure(db, doc_id, user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/{doc_id}/status")
def get_document_status(doc_id: str, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = models_and_crud.get_document_secure(db, doc_id, user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": doc.status}

@router.get("/{doc_id}/entities")
def get_document_entities(doc_id: str, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = models_and_crud.get_document_secure(db, doc_id, user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return models_and_crud.get_entities_by_document(db, doc_id)

@router.delete("/{doc_id}")
def delete_document(doc_id: str, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    success = models_and_crud.delete_document(db, doc_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete document")
    return {"detail": "Document deleted successfully"}

