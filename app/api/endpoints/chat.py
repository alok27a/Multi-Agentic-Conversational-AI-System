from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.session import get_database
from app.schemas.message import ChatRequest, ChatResponse, ResetRequest
from app.schemas.conversation import ConversationCreate, Message
from app.crud import crud_conversation, crud_user
from app.services.llm_service import get_llm_response
from app.services.rag_service import rag_service
import time

router = APIRouter()

@router.post("/", response_model=ChatResponse, tags=["Chat"])
async def handle_chat(request: ChatRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Accepts a user message, gets a response from the LLM (with RAG context),
    and logs the interaction.
    """
    start_time = time.time()

    user = await crud_user.get_user_by_id(db, user_id=request.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found. Please create a user first.")

    conversation = await crud_conversation.get_conversation_by_session_id(db, session_id=request.session_id)
    if not conversation:
        new_convo_data = ConversationCreate(user_id=request.user_id, id=request.session_id)
        conversation = await crud_conversation.create_conversation(db, new_convo_data)
    
    conversation_history = [msg.dict() for msg in conversation.messages]

    rag_context = await rag_service.retrieve_context(request.message)
    

    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    
    system_prompt = (
        "You are a helpful real estate assistant. Your task is to answer the user's questions based on the provided context.\n"
        "The context includes the previous conversation history and a list of retrieved property listings.\n"
        "Use the conversation history to understand follow-up questions. Use the property listings to answer questions about the properties.\n\n"
        f"--- Previous Conversation ---\n{history_str}\n\n"
        f"--- Retrieved Property Listings ---\n{rag_context}\n\n"
        "--- INSTRUCTIONS ---\n"
        f"Based on all the context above, provide a clear and accurate answer to the user's LATEST message: '{request.message}'.\n"
        "If the user asks for properties at an address, list all matching properties with their key details (Unit, SqFt, Rent). Do not summarize unless asked."
    )

    llm_response = await get_llm_response(system_prompt, conversation_history)

    user_message = Message(role="user", content=request.message)
    assistant_message = Message(role="assistant", content=llm_response)
    
    await crud_conversation.add_message_to_conversation(db, session_id=request.session_id, message=user_message)
    await crud_conversation.add_message_to_conversation(db, session_id=request.session_id, message=assistant_message)

    end_time = time.time()
    processing_time = round(end_time - start_time, 2)

    return ChatResponse(
        response=llm_response,
        session_id=request.session_id,
        processing_time=processing_time,
    )

@router.post("/reset", tags=["Chat"])
async def reset_conversation(request: ResetRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Clears the conversation memory for a given session by deleting it.
    A new one will be created on the next chat message.
    """
    conversation = await crud_conversation.get_conversation_by_session_id(db, session_id=request.session_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session ID not found.")
    
    await db["conversations"].delete_one({"id": request.session_id})
    
    return {"message": f"Conversation memory for session {request.session_id} has been cleared."}
