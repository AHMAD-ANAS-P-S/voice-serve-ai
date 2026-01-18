from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.enums import ApplicationStatus

class ApplicationBase(BaseModel):
    scheme_name: str
    status: ApplicationStatus = ApplicationStatus.DRAFT
    data: dict = {}
    receipt_id: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    user_id: UUID

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    data: Optional[dict] = None
    receipt_id: Optional[str] = None
    submitted_at: Optional[datetime] = None

class ApplicationResponse(ApplicationBase):
    id: UUID
    user_id: UUID
    submitted_at: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
