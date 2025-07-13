from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.session import get_database
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.schemas.conversation import ConversationInDB
from app.crud import crud_user, crud_conversation
from typing import List

router = APIRouter()

@router.post("/users", response_model=UserInDB, status_code=status.HTTP_201_CREATED, tags=["CRM"])
async def create_new_user(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    db_user = await crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    return await crud_user.create_user(db=db, user=user)


@router.get("/users/by_email", response_model=UserInDB, tags=["CRM"])
async def get_user_by_email_endpoint(email: str = Query(...), db: AsyncIOMotorDatabase = Depends(get_database)):
    """Fetches a user's profile by their email address."""
    db_user = await crud_user.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User with this email not found.")
    return db_user
# -----------------------------------------

@router.put("/users/{user_id}", response_model=UserInDB, tags=["CRM"])
async def update_existing_user(user_id: str, user_update: UserUpdate, db: AsyncIOMotorDatabase = Depends(get_database)):
    db_user = await crud_user.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return await crud_user.update_user(db=db, user_id=user_id, user_update=user_update)

@router.get("/conversations/{user_id}", response_model=List[ConversationInDB], tags=["CRM"])
async def get_user_conversations(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    db_user = await crud_user.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return await crud_conversation.get_conversations_by_user_id(db=db, user_id=user_id)
