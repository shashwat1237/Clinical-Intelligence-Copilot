from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class DocumentResponse(BaseModel):
    id: UUID          
    filename: str
    status: str
    storage_path: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)