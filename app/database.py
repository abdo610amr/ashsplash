import os
from motor.motor_asyncio import AsyncIOMotorClient

client = None
db = None


async def connect_to_mongo():
    global client, db

    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise RuntimeError("❌ MONGODB_URI is not set")

    db_name = os.getenv("DB_NAME", "ecommerce")

    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]

    await client.admin.command("ping")
    print("✅ Connected to MongoDB")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("🛑 MongoDB connection closed")


def get_database():   # ✅ الدالة الناقصة (مهمة جدًا)
    if db is None:
        raise RuntimeError("❌ Database not initialized")
    return db
