from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.user import UserCreate, UserUpdate, UserInDBBase, User
from app.core.security import get_password_hash
from typing import Optional

async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[UserInDBBase]:
    user = await db["users"].find_one({"email": email})
    return UserInDBBase(**user) if user else None

async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[User]:
    user = await db["users"].find_one({"id": user_id})
    return User(**user) if user else None

async def create_user(db: AsyncIOMotorDatabase, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = UserInDBBase(**user_in.dict(exclude={"password"}), hashed_password=hashed_password)
    await db["users"].insert_one(db_user.dict())
    return User(**db_user.dict())

async def update_user(db: AsyncIOMotorDatabase, user_id: str, user_update: UserUpdate) -> Optional[User]:
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    if not update_data:
        return await get_user_by_id(db, user_id)
    await db["users"].update_one({"id": user_id}, {"$set": update_data})
    updated_user = await db["users"].find_one({"id": user_id})
    return User(**updated_user) if updated_user else None

