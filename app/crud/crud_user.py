from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from typing import Optional

async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[UserInDB]:
    """Fetch a single user by email from the database."""
    user = await db["users"].find_one({"email": email})
    if user:
        return UserInDB(**user)
    return None

async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[UserInDB]:
    """Fetch a single user by ID from the database."""
    user = await db["users"].find_one({"id": user_id})
    if user:
        return UserInDB(**user)
    return None

async def create_user(db: AsyncIOMotorDatabase, user: UserCreate) -> UserInDB:
    """Create a new user in the database."""
    new_user = UserInDB(**user.dict())
    await db["users"].insert_one(new_user.dict())
    return new_user

async def update_user(db: AsyncIOMotorDatabase, user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
    """Update an existing user's information."""
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    if not update_data:
        return await get_user_by_id(db, user_id)

    await db["users"].update_one({"id": user_id}, {"$set": update_data})
    
    updated_user = await db["users"].find_one({"id": user_id})
    if updated_user:
        return UserInDB(**updated_user)
    return None
