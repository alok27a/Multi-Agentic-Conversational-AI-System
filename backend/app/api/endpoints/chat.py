from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.session import get_database
from app.schemas.message import ChatRequest, ChatResponse, ResetRequest
from app.schemas.conversation import ConversationCreate, Message
from app.crud import crud_conversation, crud_user
from app.services.llm_service import generate_tags_for_conversation
from app.services.langchain_agent import invoke_agent # Import the new agent invoker
import time

router = APIRouter()

async def update_tags_in_background(session_id: str, db: AsyncIOMotorDatabase):
    conversation = await crud_conversation.get_conversation_by_session_id(db, session_id)
    if conversation:
        history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in conversation.messages])
        tags = await generate_tags_for_conversation(history_str)
        if tags:
            await crud_conversation.update_conversation_tags(db, session_id, tags)
            print(f"Updated tags for session {session_id}: {tags}")

@router.post("/", response_model=ChatResponse, tags=["Chat"])
async def handle_chat(request: ChatRequest, background_tasks: BackgroundTasks, db: AsyncIOMotorDatabase = Depends(get_database)):
    start_time = time.time()

    await crud_user.get_user_by_id(db, user_id=request.user_id)

    conversation = await crud_conversation.get_conversation_by_session_id(db, session_id=request.session_id)
    if not conversation:
        new_convo_data = ConversationCreate(user_id=request.user_id, id=request.session_id)
        await crud_conversation.create_conversation(db, new_convo_data)
    
    # The LangChain agent's memory will handle the history, but we can pass it for logging/display
    conversation_history = [msg.dict() for msg in (conversation.messages if conversation else [])]

    # --- NEW: Invoke the LangChain SQL Agent ---
    llm_response = await invoke_agent(request.message, conversation_history)
    # -----------------------------------------
    
    user_message = Message(role="user", content=request.message)
    assistant_message = Message(role="assistant", content=llm_response)
    await crud_conversation.add_message_to_conversation(db, session_id=request.session_id, message=user_message)
    await crud_conversation.add_message_to_conversation(db, session_id=request.session_id, message=assistant_message)
    
    # Trigger tag generation in the background
    if len(conversation_history) > 0 and len(conversation_history) % 4 == 0:
         background_tasks.add_task(update_tags_in_background, request.session_id, db)

    end_time = time.time()
    processing_time = round(end_time - start_time, 2)

    return ChatResponse(
        response=llm_response,
        session_id=request.session_id,
        processing_time=processing_time,
    )

@router.post("/reset", tags=["Chat"])
async def reset_conversation(request: ResetRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    conversation = await crud_conversation.get_conversation_by_session_id(db, session_id=request.session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Session ID not found.")
    await db["conversations"].delete_one({"id": request.session_id})
    return {"message": f"Conversation memory for session {request.session_id} has been cleared."}
