from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str

class CitationSchema(BaseModel):
    document_name: str
    page_number: int
    excerpt: str

class ChatMessageResponse(BaseModel):
    role: str
    content: str
    citations: Optional[List[CitationSchema]] = []

    model_config = ConfigDict(from_attributes=True)