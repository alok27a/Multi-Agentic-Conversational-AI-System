from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class DBMongo:
    client: AsyncIOMotorClient = None

db = DBMongo()

async def get_database():
    """
    Returns the database instance from the client.
    """
    if db.client is None:
        await connect_to_mongo()
    return db.client[settings.DB_NAME]

async def connect_to_mongo():
    """
    Establishes the connection to the MongoDB database.
    """
    print("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.MONGO_URI)
    print("Successfully connected to MongoDB.")

async def close_mongo_connection():
    """
    Closes the MongoDB connection.
    """
    if db.client:
        print("Closing MongoDB connection...")
        db.client.close()
        print("MongoDB connection closed.")
