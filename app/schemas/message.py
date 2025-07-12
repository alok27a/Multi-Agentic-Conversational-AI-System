from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    user_id: str = Field(..., example="user_abc_123")
    session_id: str = Field(..., example="session_xyz_789")
    message: str = Field(..., example="What can you tell me about your new product?")

class ChatResponse(BaseModel):
    response: str
    session_id: str
    processing_time: float

class ResetRequest(BaseModel):
    session_id: str = Field(..., example="session_xyz_789")
