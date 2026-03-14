from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

client: AsyncIOMotorClient | None = None


async def connect_to_mongo() -> None:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.mongodb_uri)


async def close_mongo_connection() -> None:
    global client
    if client is not None:
        client.close()
        client = None
