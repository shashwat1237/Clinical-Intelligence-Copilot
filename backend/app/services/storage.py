from supabase import create_client, Client
from app.core.config import settings
from app.core.config import logger

# Initialize singleton communication instance safely
supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def upload_pdf(file_bytes: bytes, filename: str, user_id: str) -> str:
    """
    Updates the storage engine bucket with explicit headers.
    Scopes the path by user_id to prevent cross-tenant collisions.
    """
    bucket = settings.SUPABASE_BUCKET
    
    # Create a secure, isolated storage path
    safe_storage_path = f"{user_id}/{filename}"
    
    try:
        # FIX: Passed raw bytes directly to supabase-py. 
        # Removing io.BytesIO() wrapper prevents strict type-checking failures 
        # inside underlying httpx requests in recent supabase-py versions.
        supabase_client.storage.from_(bucket).upload(
            path=safe_storage_path,
            file=file_bytes,
            file_options={"content-type": "application/pdf"}
        )
        # Return the path so the DB can store it and download_pdf can retrieve it
        return safe_storage_path
    except Exception as e:
        logger.error(f"Storage upload failed for {filename}: {e}")
        raise

def download_pdf(storage_path: str) -> bytes:
    """
    Retrieves the raw binary data of a PDF from Supabase Storage.
    Required by the PyMuPDF engine during the background extraction workflow.
    """
    bucket = settings.SUPABASE_BUCKET
    try:
        # Download returns raw bytes
        response = supabase_client.storage.from_(bucket).download(storage_path)
        return response
    except Exception as e:
        logger.error(f"Storage download failed for path {storage_path}: {e}")
        raise
