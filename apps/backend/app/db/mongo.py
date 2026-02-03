from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    
mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    print(f"✅ Connected to MongoDB at {settings.MONGODB_URL}")
    
async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("❌ Closed MongoDB connection")

def get_database():
    return mongodb.client[settings.DATABASE_NAME]
