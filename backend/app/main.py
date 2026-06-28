import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import logger
from app.db.session import engine, SessionLocal
from app.db import models_and_crud

# Import routers (Ensure these files do not have top-level ML imports like `import torch`!)
from app.api.v1 import auth, upload, docs_and_reports, chat, timeline, search_and_patients

def resume_stuck_documents():
    """Recovers documents interrupted by container lifecycle actions or server restarts."""
    db = SessionLocal()
    try:
        stuck_docs = db.query(models_and_crud.Document).filter(
            models_and_crud.Document.status.in_(["QUEUED", "PROCESSING", "EXTRACTING", "INDEXING"])
        ).all()
        
        if stuck_docs:
            logger.info(f"System Recovery: Found {len(stuck_docs)} stuck documents. Resuming workflows...")
            
            # 🚨 CRITICAL FIX: LAZY IMPORT 🚨
            # Moving this here prevents it from dragging heavy ML extraction libraries into Uvicorn's boot sequence
            from app.services.extraction import process_document_workflow
            
            for doc in stuck_docs:
                patient = db.query(models_and_crud.Patient).filter(models_and_crud.Patient.id == doc.patient_id).first()
                if patient:
                    # Fire and forget recovery thread to protect main event loop speed
                    threading.Thread(
                        target=process_document_workflow, 
                        args=(doc.id, doc.storage_path, patient.id, patient.user_id)
                    ).start()
    except Exception as e:
        logger.error(f"Critical System Recovery Failure: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Enforce safe pre-allocation of pgvector extension at connection layer
    with engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
    
    # Initialize unified persistence layer models cleanly
    models_and_crud.Base.metadata.create_all(bind=engine)
    
    # Run the structural job recovery script immediately upon bootstrap completion
    resume_stuck_documents()
    yield

app = FastAPI(title="Clinical Intelligence Copilot API", version="1.0.0", lifespan=lifespan)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Strict CORS routing configuration mapping
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL], 
    allow_credentials=False,  # Set to False to fulfill strict ASGI/Starlette security isolation policies
    allow_methods=["*"],
    allow_headers=["*"],
)

# Explicitly assign consolidated routing blocks to protect architecture limits
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(docs_and_reports.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(search_and_patients.router, prefix="/api/v1/patients", tags=["Patients & Search"])
app.include_router(timeline.router, prefix="/api/v1/timeline", tags=["Timeline"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])

@app.get("/api/v1/health", status_code=200)
def health_check():
    """Remediates infrastructure probe failures for active platform routing verification."""
    return {"status": "healthy", "service": "clinical-intelligence-copilot"}
