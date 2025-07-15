from pymongo import AsyncMongoClient

from src.settings import MONGODB_DATABASE


async def create_indexes(client: AsyncMongoClient):
    database = client[MONGODB_DATABASE]
    collection = database['normalized_data']
    await collection.create_index("platform")
    await collection.create_index("last_seen_at")
    await collection.create_index("open_ports.port")
