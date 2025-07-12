from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.session import get_database
from app.schemas.message import ChatRequest, ChatResponse, ResetRequest
from app.schemas.conversation import ConversationCreate, Message
from app.crud import crud_conversation, crud_user
from app.services.llm_service import generate_sql_from_prompt, synthesize_response_from_sql, generate_tags_for_conversation
from app.services.text_to_sql_service import text_to_sql_service
import time

router = APIRouter()

async def update_tags_in_background(session_id: str, db: AsyncIOMotorDatabase):
    """A background task to generate and save conversation tags."""
    # Refetch the latest history to ensure it's complete
    conversation = await crud_conversation.get_conversation_by_session_id(db, session_id)
    if conversation:
        history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in conversation.messages])
        tags = await generate_tags_for_conversation(history_str)
        if tags:
            await crud_conversation.update_conversation_tags(db, session_id, tags)
            print(f"Updated tags for session {session_id}: {tags}")

@router.post("/", response_model=ChatResponse, tags=["Chat"])
async def handle_chat(request: ChatRequest, background_tasks: BackgroundTasks, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Handles the Text-to-SQL conversation flow and CRM tagging."""
    start_time = time.time()

    # 1. Verify user
    await crud_user.get_user_by_id(db, user_id=request.user_id)

    # 2. Get conversation history
    conversation = await crud_conversation.get_conversation_by_session_id(db, session_id=request.session_id)
    if not conversation:
        new_convo_data = ConversationCreate(user_id=request.user_id, id=request.session_id)
        conversation = await crud_conversation.create_conversation(db, new_convo_data)
    
    history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in conversation.messages])

    # 3. Get DB Schema
    schema = text_to_sql_service.get_schema()
    if "No schema loaded" in schema:
        raise HTTPException(status_code=400, detail="Knowledge base not loaded. Please upload a CSV file first.")

    # 4. Generate SQL
    sql_generation_prompt = (
        f"Schema:\n{schema}\n\nConversation History:\n{history_str}\n\nUser's Latest Question: '{request.message}'\n\nQuery:"
    )
    generated_sql = await generate_sql_from_prompt(sql_generation_prompt)

    # 5. Execute SQL
    sql_results = text_to_sql_service.execute_sql_query(generated_sql)

    # 6. Synthesize Response
    llm_response = await synthesize_response_from_sql(request.message, generated_sql, sql_results)
    
    # 7. Log messages to CRM
    user_message = Message(role="user", content=request.message)
    assistant_message = Message(role="assistant", content=llm_response)
    await crud_conversation.add_message_to_conversation(db, session_id=request.session_id, message=user_message)
    await crud_conversation.add_message_to_conversation(db, session_id=request.session_id, message=assistant_message)
    
    # 8. Trigger background task to update tags
    # This runs after the response is sent to the user, so it doesn't slow down the chat.
    if len(conversation.messages) % 4 == 0: # Update tags every few turns
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
