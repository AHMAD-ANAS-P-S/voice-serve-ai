from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.enums import DocumentType

class DocumentBase(BaseModel):
    doc_type: DocumentType
    ocr_data: dict = {}
    verified: bool = False

class DocumentCreate(DocumentBase):
    user_id: UUID

class DocumentUpdate(BaseModel):
    ocr_data: Optional[dict] = None
    verified: Optional[bool] = None

class DocumentResponse(DocumentBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
