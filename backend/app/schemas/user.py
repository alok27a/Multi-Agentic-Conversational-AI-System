from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    name: Optional[str] = Field(None, example="John Doe")
    company: Optional[str] = Field(None, example="Example Inc.")

class UserCreate(UserBase):
    password: str = Field(..., example="a_strong_password")

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, example="John Doe")
    company: Optional[str] = Field(None, example="Example Inc.")

# This model is used when storing the user in the database
class UserInDBBase(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hashed_password: str

# This model is used when returning user data from the API (omits password)
class User(UserBase):
    id: str
    class Config:
        from_attributes = True
