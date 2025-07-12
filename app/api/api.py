from fastapi import APIRouter
from app.api.endpoints import chat, crm, documents

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(crm.router, prefix="/crm", tags=["CRM"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])