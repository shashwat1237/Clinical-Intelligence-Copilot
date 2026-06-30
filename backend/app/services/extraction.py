import gc
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db import models_and_crud
from app.services.storage import download_pdf
from app.ai.extraction import extract_clinical_entities_from_text
from app.ai.embeddings import VectorIndexer
from app.core.config import logger

def process_document_workflow(doc_id: str, storage_path: str, patient_id: str, user_id: str):
    """Asynchronous orchestrator executing structured extraction with OCR fallback and localized chunk vectors."""
    db: Session = SessionLocal()
    try:
        models_and_crud.update_document_status(db, doc_id, "PROCESSING")
        
        pdf_bytes = download_pdf(storage_path)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        pages_text = []
        
        # Enforce deterministic overlapping window properties
        CHUNK_SIZE = 300 
        OVERLAP = 50

        for page_num in range(len(doc)):
            page_text = doc[page_num].get_text()
            
            # ==========================================
            # SMART OCR FALLBACK MECHANISM
            # ==========================================
            # If the page text is practically empty (scanned image), trigger OCR
            if len(page_text.strip()) < 100:
                logger.info(f"Insufficient text detected on page {page_num + 1} of document {doc_id}. Triggering OCR...")
                try:
                    # Render page to high-res image (matrix scales by 2x for better OCR accuracy)
                    pix = doc[page_num].get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Extract text from the image buffer
                    ocr_text = pytesseract.image_to_string(img)
                    page_text = ocr_text
                    logger.info(f"OCR successfully recovered {len(page_text)} characters on page {page_num + 1}.")
                except Exception as ocr_e:
                    logger.warning(f"OCR fallback failed on page {page_num + 1}: {ocr_e}")
            # ==========================================

            # Replaced "n" with explicit newline character "\n" to prevent cross-page word concatenation
            full_text += page_text + "\n"
            
            words = page_text.split()
            if not words:
                continue
                
            for i in range(0, len(words), CHUNK_SIZE - OVERLAP):
                chunk_words = words[i:i + CHUNK_SIZE]
                chunk_text = " ".join(chunk_words)
                if len(chunk_words) > 15:  # Neutralize indexing empty pages or boilerplate artifact margins
                    pages_text.append({"page": page_num + 1, "content": chunk_text})
        
        # Guardrail check against dead un-extractable scanned asset payloads
        if not full_text.strip():
            logger.error(f"Ingestion Abrupt End: Document {doc_id} contains no extractable text headers even after OCR.")
            models_and_crud.update_document_status(db, doc_id, "FAILED")
            return

        models_and_crud.update_document_status(db, doc_id, "EXTRACTING")

        # Truncate text to safely stay under the 12,000 Tokens Per Minute limit.
        safe_text_payload = full_text[:25000]

        # Connect directly to extraction layer using the truncated text
        extracted_data = extract_clinical_entities_from_text(safe_text_payload)
        
        for ent in extracted_data.get("entities", []):
            models_and_crud.save_clinical_entity(db, {
                "patient_id": patient_id,
                "document_id": doc_id,
                "category": ent["category"],
                "normalized_name": ent["normalized_name"],
                "value": ent.get("value", ""),
                "metadata_json": ent.get("metadata", {})
            })
            
        for event in extracted_data.get("timeline", []):
            models_and_crud.save_timeline_event(db, {
                "patient_id": patient_id,
                "document_id": doc_id,
                "date": event["date"],
                "event_type": event["event_type"],
                "description": event["description"]
            })

        models_and_crud.update_document_status(db, doc_id, "INDEXING")

        # OOM RESOLUTION: Pre-ML Memory Purge
        del pdf_bytes
        del full_text
        del safe_text_payload
        doc.close()
        del doc
        gc.collect()

        # Map vector space generation cleanly
        indexer = VectorIndexer()
        indexer.index_document(db, doc_id, patient_id, pages_text)

        models_and_crud.update_document_status(db, doc_id, "READY")
        logger.info(f"Ingestion Success: Document {doc_id} normalized and fully live.")
        
    except Exception as e:
        logger.error(f"Ingestion Core Pipeline Failure on {doc_id}: {str(e)}")
        
        # Rollback the broken database transaction first
        db.rollback() 
        
        try:
            models_and_crud.update_document_status(db, doc_id, "FAILED")
        except Exception as inner_e:
            logger.warning(f"Could not update status (Document likely purged by user): {inner_e}")
            
    finally:
        db.close()
