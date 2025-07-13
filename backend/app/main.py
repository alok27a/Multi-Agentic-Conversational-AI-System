from fastapi import FastAPI
from app.core.config import settings
from app.api.api import api_router
from app.db.session import close_mongo_connection, connect_to_mongo

app = FastAPI(
    title="Multi-Agentic Conversational AI System",
    description="A FastAPI application with an LLM, RAG, and a CRM.",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup."""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown."""
    await close_mongo_connection()

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the Multi-Agentic Conversational AI API!"}