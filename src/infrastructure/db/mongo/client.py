from pymongo import AsyncMongoClient

from src.settings import MONGODB_URL


def get_mongo_client() -> AsyncMongoClient:
    return AsyncMongoClient(MONGODB_URL)
