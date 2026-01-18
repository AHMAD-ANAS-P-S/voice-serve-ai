from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from app.models.enums import DomainType, ConversationStatus, MessageRole

# Message Schemas
class MessageBase(BaseModel):
    role: MessageRole
    content: str
    voice_url: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: UUID
    conversation_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Conversation Schemas
class ConversationBase(BaseModel):
    domain: DomainType
    status: ConversationStatus = ConversationStatus.ACTIVE

class ConversationCreate(ConversationBase):
    user_id: UUID

class ConversationUpdate(BaseModel):
    status: Optional[ConversationStatus] = None

class ConversationResponse(ConversationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    messages: List[MessageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
