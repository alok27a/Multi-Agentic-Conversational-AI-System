from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.conversation import ConversationCreate, ConversationInDB, Message
from typing import List, Optional

async def create_conversation(db: AsyncIOMotorDatabase, conversation: ConversationCreate) -> ConversationInDB:
    convo_data = conversation.dict()
    await db["conversations"].insert_one(convo_data)
    return ConversationInDB(**convo_data)

async def get_conversation_by_session_id(db: AsyncIOMotorDatabase, session_id: str) -> Optional[ConversationInDB]:
    convo_data = await db["conversations"].find_one({"id": session_id})
    return ConversationInDB(**convo_data) if convo_data else None

async def add_message_to_conversation(db: AsyncIOMotorDatabase, session_id: str, message: Message):
    await db["conversations"].update_one({"id": session_id}, {"$push": {"messages": message.dict()}})

async def update_conversation_tags(db: AsyncIOMotorDatabase, session_id: str, tags: List[str]):
    """Updates the tags for a given conversation."""
    await db["conversations"].update_one({"id": session_id}, {"$set": {"tags": tags}})

async def get_conversations_by_user_id(db: AsyncIOMotorDatabase, user_id: str) -> List[ConversationInDB]:
    conversations = []
    cursor = db["conversations"].find({"user_id": user_id})
    async for document in cursor:
        conversations.append(ConversationInDB(**document))
    return conversations