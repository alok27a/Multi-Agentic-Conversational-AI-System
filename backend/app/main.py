from fastapi import FastAPI
from app.core.config import settings
from app.api.api import api_router
from app.db.session import close_mongo_connection, connect_to_mongo
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Multi-Agentic Conversational AI System",
    description="A FastAPI application with an LLM, RAG, and a CRM.",
    version="1.0.0",
)

# --- CORS MIDDLEWARE SETUP ---
origins = [
    "http://localhost",
    "http://localhost:3000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)
# -----------------------------

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