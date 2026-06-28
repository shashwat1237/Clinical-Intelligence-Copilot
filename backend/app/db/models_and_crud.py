import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Integer, select
from sqlalchemy.orm import relationship, Session
from pgvector.sqlalchemy import Vector
from app.db.session import Base

# =========================================================================
# SCHEMA DEFINITIONS
# =========================================================================

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    patient = relationship("Patient", back_populates="user", uselist=False)

class Patient(Base):
    __tablename__ = "patients"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    user = relationship("User", back_populates="patient")
    documents = relationship("Document", back_populates="patient")

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    filename = Column(String)
    storage_path = Column(String)
    status = Column(String, default="QUEUED")  # QUEUED, PROCESSING, EXTRACTING, INDEXING, READY, FAILED
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    patient = relationship("Patient", back_populates="documents")

class VectorChunk(Base):
    __tablename__ = "vector_chunks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"))
    patient_id = Column(String, ForeignKey("patients.id"))
    page = Column(Integer)
    content = Column(String)
    embedding = Column(Vector(384))  # Perfectly scaled to store local 384-dim dimensions

class ClinicalEntity(Base):
    __tablename__ = "clinical_entities"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    document_id = Column(String, ForeignKey("documents.id"))
    category = Column(String) 
    normalized_name = Column(String)
    value = Column(String, nullable=True)
    metadata_json = Column(JSON, default={})

class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    document_id = Column(String, ForeignKey("documents.id"))
    date = Column(String)
    event_type = Column(String)
    description = Column(String)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    role = Column(String)
    content = Column(String)
    citations_json = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

# =========================================================================
# DATA ACCESS EXTENSION METRICS
# =========================================================================

def create_user(db: Session, user_id: str, email: str):
    db_user = User(id=user_id, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_patient_profile(db: Session, user_id: str):
    db_patient = Patient(user_id=user_id)
    db.add(db_patient)
    db.commit()
    return db_patient

def get_patient_by_user(db: Session, user_id: str):
    return db.query(Patient).filter(Patient.user_id == user_id).first()

def create_document(db: Session, patient_id: str, filename: str, storage_path: str):
    doc = Document(patient_id=patient_id, filename=filename, storage_path=storage_path)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_documents_by_patient(db: Session, patient_id: str):
    return db.query(Document).filter(Document.patient_id == patient_id).order_by(Document.uploaded_at.desc()).all()

def get_document_secure(db: Session, doc_id: str, user_id: str):
    """Enforces absolute user verification check layers to neutralize permission bypass attempts."""
    return db.query(Document).join(Patient).filter(Document.id == doc_id, Patient.user_id == user_id).first()

def update_document_status(db: Session, doc_id: str, status: str):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc:
        doc.status = status
        db.commit()

def delete_document(db: Session, doc_id: str, user_id: str) -> bool:
    doc = get_document_secure(db, doc_id, user_id)
    if not doc:
        return False
    try:
        # Enforce explicitly un-synchronized deletes to optimize transaction isolation locks in SQLAlchemy 2.0
        db.query(ClinicalEntity).filter(ClinicalEntity.document_id == doc_id).delete(synchronize_session=False)
        db.query(TimelineEvent).filter(TimelineEvent.document_id == doc_id).delete(synchronize_session=False)
        db.query(VectorChunk).filter(VectorChunk.document_id == doc_id).delete(synchronize_session=False)
        db.delete(doc)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False

def save_clinical_entity(db: Session, entity_data: dict):
    entity = ClinicalEntity(**entity_data)
    db.add(entity)
    db.commit()

def save_timeline_event(db: Session, event_data: dict):
    event = TimelineEvent(**event_data)
    db.add(event)
    db.commit()

def get_entities_by_document(db: Session, doc_id: str):
    return db.query(ClinicalEntity).filter(ClinicalEntity.document_id == doc_id).all()

def get_entities_by_category(db: Session, patient_id: str, category: str):
    return db.query(ClinicalEntity).filter(ClinicalEntity.patient_id == patient_id, ClinicalEntity.category == category).all()

def get_timeline_for_patient(db: Session, patient_id: str):
    return db.query(TimelineEvent).filter(TimelineEvent.patient_id == patient_id).order_by(TimelineEvent.date.desc()).all()

def save_chat_message(db: Session, patient_id: str, role: str, content: str, citations: list = []):
    msg = ChatMessage(patient_id=patient_id, role=role, content=content, citations_json=citations)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_chat_history(db: Session, patient_id: str):
    return db.query(ChatMessage).filter(ChatMessage.patient_id == patient_id).order_by(ChatMessage.created_at.asc()).all()
