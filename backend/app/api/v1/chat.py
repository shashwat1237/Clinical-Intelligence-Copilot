from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatMessageResponse
from app.services.chat import ChatService
from app.db import models_and_crud

router = APIRouter()

@router.post("", response_model=ChatMessageResponse)
def chat_with_copilot(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = models_and_crud.get_patient_by_user(db, user_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile missing.")
        
    chat_service = ChatService(db, user_id, patient.id)
    response = chat_service.process_user_query(request.message)
    return response

@router.get("/history", response_model=List[ChatMessageResponse])
def get_chat_history(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = models_and_crud.get_patient_by_user(db, user_id)
    history = models_and_crud.get_chat_history(db, patient.id)
    
    # Map the 'citations_json' DB column to the 'citations' field expected by the frontend
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "citations": msg.citations_json
        } for msg in history
    ]

@router.delete("/")
def clear_chat_history(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = models_and_crud.get_patient_by_user(db, user_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile missing.")
    
    # Wipe all messages for this patient
    db.query(models_and_crud.ChatMessage).filter(
        models_and_crud.ChatMessage.patient_id == patient.id
    ).delete(synchronize_session=False)
    db.commit()
    
    return {"detail": "Telemetry log purged successfully"}
