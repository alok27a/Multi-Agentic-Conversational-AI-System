import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Application settings loaded from environment variables.
    """
    PROJECT_NAME: str = "Multi-Agentic Conversational AI System"
    API_V1_STR: str = "/api/v1"

    # OpenAI Credentials
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    # MongoDB Credentials
    MONGO_URI: str = os.getenv("MONGO_URI")
    DB_NAME: str = os.getenv("DB_NAME")

settings = Settings()
