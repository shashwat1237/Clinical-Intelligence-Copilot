import os
import logging
from pydantic_settings import BaseSettings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("clinical_copilot")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Clinical Intelligence Copilot"
    DATABASE_URL: str = "postgresql://localhost/clinical_copilot"
    GROQ_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str  # <-- CHANGED THIS LINE
    SUPABASE_BUCKET: str = "medical-reports"
    JWT_SECRET: str  

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

if settings.DATABASE_URL.startswith("postgresql://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)