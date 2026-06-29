from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError  # Use local cryptographic validation
import logging

from app.core.config import settings

logger = logging.getLogger("clinical_copilot")
oauth2_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> str:
    token = credentials.credentials
    try:
        # 🚨 CRITICAL FIX: Local JWT Validation
        # Instead of making a fragile network request to Supabase on every API call,
        # we verify the token cryptographically in-memory using your Supabase JWT Secret.
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase uses 'authenticated' audience by default
        )
        
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise ValueError("Token validation returned empty user subject.")
            
        return user_id
        
    except Exception as e:
        logger.error(f"Auth Rejection (Local Validation): {str(e)}") 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
