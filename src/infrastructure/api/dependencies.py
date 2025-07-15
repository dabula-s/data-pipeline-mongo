from src.core.ports.repositories import HostNormalizedDataRepository
from src.infrastructure.db.mongo.client import get_mongo_client
from src.infrastructure.db.mongo.repositories import MongoHostNormalizedDataRepository


def get_normal_repository() -> HostNormalizedDataRepository:
    return MongoHostNormalizedDataRepository(client=get_mongo_client())
