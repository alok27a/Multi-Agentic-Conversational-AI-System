from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.conversation import ConversationCreate, ConversationInDB, Message
from typing import List, Optional

async def create_conversation(db: AsyncIOMotorDatabase, conversation: ConversationCreate) -> ConversationInDB:
    """
    Create a new conversation record.
    The conversation object already contains the ID (session_id).
    """
    convo_data = conversation.dict()
    await db["conversations"].insert_one(convo_data)
    # Return the same object, as it's already what's in the DB
    return ConversationInDB(**convo_data)

async def get_conversation_by_session_id(db: AsyncIOMotorDatabase, session_id: str) -> Optional[ConversationInDB]:
    """Retrieve a conversation by its session ID."""
    convo_data = await db["conversations"].find_one({"id": session_id})
    if convo_data:
        return ConversationInDB(**convo_data)
    return None

async def add_message_to_conversation(db: AsyncIOMotorDatabase, session_id: str, message: Message):
    """Add a new message to an existing conversation."""
    await db["conversations"].update_one(
        {"id": session_id},
        {"$push": {"messages": message.dict()}}
    )

async def get_conversations_by_user_id(db: AsyncIOMotorDatabase, user_id: str) -> List[ConversationInDB]:
    """Retrieve all conversations for a specific user."""
    conversations = []
    cursor = db["conversations"].find({"user_id": user_id})
    async for document in cursor:
        conversations.append(ConversationInDB(**document))
    return conversations
