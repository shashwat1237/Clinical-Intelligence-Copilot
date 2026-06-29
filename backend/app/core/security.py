from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import logging
import time

from app.core.config import settings

logger = logging.getLogger("clinical_copilot")
oauth2_scheme = HTTPBearer()

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> str:
    token = credentials.credentials
    
    # 🚨 CRITICAL FIX: The Render SSL Resilience Loop
    # Render kills idle connections, causing "EOF occurred in violation of protocol".
    # We wrap the official Supabase auth check in a retry block. If a stale connection dies, 
    # the retry instantly forces the underlying HTTP client to open a fresh connection.
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            user_response = supabase.auth.get_user(token)
            
            if not user_response or not getattr(user_response, 'user', None):
                raise ValueError("Token validation returned empty user.")
                
            return user_response.user.id
            
        except Exception as e:
            error_msg = str(e)
            
            # If it's a network/SSL drop, we swallow the error and retry cleanly
            if "EOF" in error_msg or "SSL" in error_msg or "Connection" in error_msg:
                if attempt < max_retries - 1:
                    logger.warning(f"Supabase connection dropped by Render. Retrying {attempt + 1}/{max_retries}...")
                    time.sleep(0.5)  # Brief micro-pause to let the socket reset
                    continue
            
            # If we exhausted retries OR it's a true auth failure (e.g., expired token)
            logger.error(f"Supabase Auth Rejection: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
