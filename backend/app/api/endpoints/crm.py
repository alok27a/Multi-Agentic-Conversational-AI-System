from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.session import get_database
from app.schemas.user import UserCreate, UserUpdate, User
from app.crud import crud_user
from app.schemas.conversation import ConversationInDB
from app.crud import crud_conversation
from app.core.security import verify_password
from app.services.text_to_sql_service import text_to_sql_service
from typing import List
import os
import shutil

router = APIRouter()

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED, tags=["CRM"])
async def create_new_user(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    db_user = await crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    return await crud_user.create_user(db=db, user_in=user)

# --- NEW COMBINED LOGIN AND UPLOAD ENDPOINT ---
@router.post("/login", response_model=User, tags=["CRM"])
async def login_and_upload(
    email: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Authenticates a user and uploads their CSV knowledge base in a single step.
    """
    # Step 1: Authenticate user
    user = await crud_user.get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Step 2: Process and save the uploaded CSV file
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        success = text_to_sql_service.load_csv_to_sql(file_path)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process and load CSV into database.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return User(**user.dict())
# -----------------------------------------

@router.get("/users/by_email", response_model=User, tags=["CRM"])
async def get_user_by_email_endpoint(email: str = Query(...), db: AsyncIOMotorDatabase = Depends(get_database)):
    db_user = await crud_user.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User with this email not found.")
    return User(**db_user.dict())

@router.put("/users/{user_id}", response_model=User, tags=["CRM"])
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
