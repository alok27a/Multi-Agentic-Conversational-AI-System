from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    role: str = Field(..., example="user") # "user" or "assistant"
    content: str = Field(..., example="Hello, how are you?")

class ConversationBase(BaseModel):
    # FIX: The conversation ID is now explicitly part of the base model.
    # This ID will be the session_id provided by the client.
    id: str = Field(..., example="session_xyz_789")
    user_id: str = Field(..., example="user_123")
    messages: List[Message] = []
    tags: Optional[List[str]] = Field(None, example=["Inquiring", "ProductA"])
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConversationCreate(ConversationBase):
    pass

class ConversationInDB(ConversationBase):
    class Config:
        from_attributes = True
