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
    
    # 🚨 CRITICAL FIX: The Render SSL & HTTP/2 Resilience Loop
    # Render kills idle connections, and rapid UI polling causes httpx HTTP/2 stream corruption.
    # We wrap the official Supabase auth check in a robust retry block.
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            user_response = supabase.auth.get_user(token)
            
            if not user_response or not getattr(user_response, 'user', None):
                raise ValueError("Token validation returned empty user.")
                
            return user_response.user.id
            
        except Exception as e:
            error_msg = str(e)
            
            # 🚀 FIXED: Now safely catches HTTP/2 Stream failures alongside SSL/EOF drops
            is_recoverable_network_error = any(
                keyword in error_msg 
                for keyword in ["EOF", "SSL", "Connection", "Stream", "state 5", "StreamIDTooLow"]
            )
            
            if is_recoverable_network_error:
                if attempt < max_retries - 1:
                    logger.warning(f"Supabase connection dropped or stream corrupted. Retrying {attempt + 1}/{max_retries}...")
                    time.sleep(0.5)  # Brief micro-pause to let the socket and httpx state machine reset
                    continue
            
            # If we exhausted retries OR it's a true auth failure (e.g., expired token)
            logger.error(f"Supabase Auth Rejection: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
