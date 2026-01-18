from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class AgentLogBase(BaseModel):
    agent_name: str
    input: dict = {}
    output: dict = {}

class AgentLogCreate(AgentLogBase):
    conversation_id: UUID

class AgentLogResponse(AgentLogBase):
    id: UUID
    conversation_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
