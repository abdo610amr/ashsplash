import os
from motor.motor_asyncio import AsyncIOMotorClient

client = None
db = None

async def connect_to_mongo():
    global client, db

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("❌ MONGO_URI is not set")

    db_name = os.getenv("DB_NAME", "ecommerce")

    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]

    await client.admin.command("ping")
    print("✅ Connected to MongoDB")
