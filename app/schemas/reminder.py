from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.enums import ReminderType

class ReminderBase(BaseModel):
    reminder_type: ReminderType
    scheduled_for: datetime
    sent: bool = False

class ReminderCreate(ReminderBase):
    user_id: UUID

class ReminderUpdate(BaseModel):
    scheduled_for: Optional[datetime] = None
    sent: Optional[bool] = None

class ReminderResponse(ReminderBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
