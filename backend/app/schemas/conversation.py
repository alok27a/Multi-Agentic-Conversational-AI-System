from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    role: str = Field(..., example="user")
    content: str = Field(..., example="Hello, how are you?")

class ConversationBase(BaseModel):
    id: str = Field(..., example="session_xyz_789")
    user_id: str = Field(..., example="user_123")
    messages: List[Message] = []
    # Added tags field for CRM categorization
    tags: List[str] = Field(default_factory=list, example=["Property Inquiry"])
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConversationCreate(ConversationBase):
    pass

class ConversationInDB(ConversationBase):
    class Config:
        from_attributes = True
