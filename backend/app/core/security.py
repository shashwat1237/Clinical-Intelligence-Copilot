from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import logging

from app.core.config import settings

logger = logging.getLogger("clinical_copilot")
oauth2_scheme = HTTPBearer()

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> str:
    token = credentials.credentials
    try:
        # Pass the token explicitly to the Supabase SDK
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not getattr(user_response, 'user', None):
            raise ValueError("Token validation returned empty user.")
            
        return user_response.user.id
        
    except Exception as e:
        logger.error(f"Supabase Auth Rejection: {str(e)}") 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )