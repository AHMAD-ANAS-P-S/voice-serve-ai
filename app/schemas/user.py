from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from .chat import ConversationResponse
from .document import DocumentResponse
from .application import ApplicationResponse
from .reminder import ReminderResponse

class UserBase(BaseModel):
    telegram_id: str
    phone: Optional[str] = None
    language_preference: str = "en"

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    language_preference: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    # Optionally include relationships if needed, avoiding circular loops
    # conversations: List[ConversationResponse] = [] 
    
    model_config = ConfigDict(from_attributes=True)
