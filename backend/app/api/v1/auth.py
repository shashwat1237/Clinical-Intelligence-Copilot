from fastapi import APIRouter, HTTPException, Depends
from supabase import create_client, Client
from app.schemas.auth import UserCredentials, TokenResponse
from app.core.config import settings
from app.db.session import get_db
from app.db import models_and_crud
from sqlalchemy.orm import Session

router = APIRouter()
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

@router.post("/signup", response_model=TokenResponse)
def signup(creds: UserCredentials, db: Session = Depends(get_db)):
    try:
        res = supabase.auth.sign_up({"email": creds.email, "password": creds.password})
        
        if not res.user:
            raise HTTPException(status_code=400, detail="Signup failed. Invalid email or password.")
            
        # CRITICAL FIX: Handle Supabase default email confirmation blocking
        if not res.session:
            raise HTTPException(
                status_code=403, 
                detail="Signup successful, but email verification is required. Please check your inbox OR disable 'Enable Email Confirmations' in your Supabase Auth settings to allow instant login."
            )
        
        # Sync user to PostgreSQL canonical DB
        user = models_and_crud.create_user(db, res.user.id, creds.email)
        models_and_crud.create_patient_profile(db, user.id)
        
        return {"access_token": res.session.access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
def login(creds: UserCredentials):
    try:
        res = supabase.auth.sign_in_with_password({"email": creds.email, "password": creds.password})
        if not res.session:
            raise HTTPException(status_code=401, detail="Invalid credentials or unverified email.")
            
        return {"access_token": res.session.access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

