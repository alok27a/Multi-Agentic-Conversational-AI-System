from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    name: Optional[str] = Field(None, example="John Doe")
    company: Optional[str] = Field(None, example="Example Inc.")
    preferences: Optional[str] = Field(None, example="Prefers concise answers.")

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, example="John Doe")
    company: Optional[str] = Field(None, example="Example Inc.")
    preferences: Optional[str] = Field(None, example="Prefers detailed explanations.")

class UserInDB(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    class Config:
        orm_mode = True
