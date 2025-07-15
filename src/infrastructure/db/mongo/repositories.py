import logging
from datetime import timedelta, datetime
from typing import AsyncIterator

from bson import ObjectId
from pymongo import AsyncMongoClient

from src.core.entities import HostNormalizedData, HostRawData, HostUnmergedDataGroup
from src.core.ports.repositories import HostRawDataRepository, HostNormalizedDataRepository
from src.settings import MONGODB_DATABASE, PIPELINE_CONFIG

logger = logging.getLogger(__name__)


class MongoHostRawDataRepository(HostRawDataRepository):
    def __init__(self, client: AsyncMongoClient):
        self.client = client
        self.database = client[MONGODB_DATABASE]

    async def save_raw_data(self, collection: str, documents: list[HostRawData]) -> None:
        logger.info(f'Saving {len(documents)} documents to {collection}')
        await self.database[collection].insert_many([document.model_dump(exclude_unset=True) for document in documents])

    async def get_raw_data(self, collection: str, batch_size: int = 10) -> AsyncIterator[list[HostRawData]]:
        batch = []
        async for document in self.database[collection].find():
            batch.append(HostRawData(**document))
            if len(batch) >= batch_size:
                logger.info(f'Fetched {len(batch)} documents from {collection}')
                yield batch
                batch = []
        if batch:
            logger.info(f'Fetched {len(batch)} documents from {collection}')
            yield batch


class MongoHostNormalizedDataRepository(HostNormalizedDataRepository):
    def __init__(self, client: AsyncMongoClient):
        self.client = client
        self.database = client[MONGODB_DATABASE]

    async def get_normalized_data(self, collection: str, batch_size: int = 10) -> AsyncIterator[
        list[HostNormalizedData]]:
        batch = []
        async for document in self.database[collection].find():
            logger.info(document)
            batch.append(HostNormalizedData(**document))
            if len(batch) >= batch_size:
                logger.debug(f'Fetched {len(batch)} documents from {collection}')
                yield batch
                batch = []
        if batch:
            logger.debug(f'Fetched {len(batch)} documents from {collection}')
            yield batch

    async def save_normalized_data(self, collection: str, documents: list[HostNormalizedData]) -> None:
        logger.debug(f'Saving {len(documents)} documents to {collection}')
        await self.database[collection].insert_many([document.model_dump() for document in documents])

    async def delete_normalized_data_by_ids(self, collection: str, ids: list[str]) -> None:
        logger.debug(f'Deleting {len(ids)} documents from {collection}')
        delete_result = await self.database[collection].delete_many({'_id': {'$in': [ObjectId(x) for x in ids]}})
        logger.debug(f'Deleted {delete_result.deleted_count} documents from {collection}')

    async def get_unmerged_docs_groups(self, collection: str, batch_size: int = 10) -> AsyncIterator[
        list[HostUnmergedDataGroup]]:
        pipeline = [
            {"$group": {
                "_id": {field: f"${field}" for field in PIPELINE_CONFIG['deduplication']['unique_keys']},
                "docs": {"$push": "$$ROOT"},
                "ids": {"$push": "$_id"},
                "count": {"$sum": 1}
            }},
            {"$match": {"count": {"$gt": 0}}}
        ]
        cursor = await self.database[collection].aggregate(pipeline)

        batch = []
        async for group in cursor:
            batch.append(HostUnmergedDataGroup(group_id=group['_id'], group_docs=group['docs']))
            if len(batch) >= batch_size:
                logger.debug(f'Fetched {len(batch)} groups from {collection}')
                yield batch
                batch = []
        if batch:
            logger.debug(f'Fetched {len(batch)} groups from {collection}')
            yield batch

    async def get_os_distribution(self, collection: str) -> dict[str, int]:
        pipeline = [
            {"$group": {"_id": "$platform", "count": {"$sum": 1}}},
            {"$match": {"_id": {"$ne": None}}},
            {"$sort": {"count": -1}},
            {"$project": {"platform": "$_id", "count": 1, "_id": 0}}
        ]
        cursor = await self.database[collection].aggregate(pipeline)
        return {doc["platform"]: doc["count"] async for doc in cursor}

    async def get_old_vs_new_hosts(self, collection: str, days_threshold: int = 30) -> dict[str, int]:
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        pipeline = [
            {"$match": {"last_seen_at": {"$ne": None}}},
            {
                "$group": {
                    "_id": {
                        "$cond": {
                            "if": {"$lte": ["$last_seen_at", threshold_date]},
                            "then": "old",
                            "else": "new"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$project": {"category": "$_id", "count": 1, "_id": 0}}
        ]
        cursor = await self.database[collection].aggregate(pipeline)
        distribution = {"old": 0, "new": 0}
        async for doc in cursor:
            distribution[doc["category"]] = doc["count"]
        return distribution

    async def get_open_ports_distribution(self, collection: str) -> dict[int, int]:
        pipeline = [
            {"$unwind": "$open_ports"},  # Unwind the open_ports array
            {
                "$group": {
                    "_id": {
                        "host_id": "$_id",  # Group by host document _id
                        "port": "$open_ports.port"  # Include port number
                    }
                }
            },  # Collect unique ports per host
            {
                "$group": {
                    "_id": "$_id.port",  # Group by port number across all hosts
                    "count": {"$sum": 1}  # Count number of hosts with this port
                }
            },
            {"$sort": {"_id": 1}},  # Sort by port number
            {
                "$project": {
                    "port": "$_id",
                    "count": 1,
                    "_id": 0
                }
            }
        ]
        cursor = await self.database[collection].aggregate(pipeline)
        result = {doc["port"]: doc["count"] async for doc in cursor}
        return result

    async def get_open_ports_by_platform_distribution(self, collection: str, ports_list: list[int]) -> dict[
        str, dict[int, int]]:
        pipeline = [
            {"$match": {"platform": {"$ne": None}, "open_ports.port": {"$in": ports_list}}},
            {"$unwind": "$open_ports"},
            {
                "$group": {
                    "_id": {
                        "host_id": "$_id",
                        "platform": "$platform",
                        "port": "$open_ports.port"
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "platform": "$_id.platform",
                        "port": "$_id.port"
                    },
                    "count": {"$sum": 1}  # Count hosts per platform and port
                }
            },
            {"$sort": {"_id.platform": 1, "_id.port": 1}},
            {
                "$group": {
                    "_id": "$_id.platform",
                    "ports": {
                        "$push": {
                            "port": "$_id.port",
                            "count": "$count"
                        }
                    }
                }
            },
            {
                "$project": {
                    "platform": "$_id",
                    "ports": {
                        "$arrayToObject": {
                            "$map": {
                                "input": "$ports",
                                "as": "item",
                                "in": {
                                    "k": {"$toString": "$$item.port"},
                                    "v": "$$item.count"
                                }
                            }
                        }
                    },
                    "_id": 0
                }
            }
        ]
        cursor = await self.database[collection].aggregate(pipeline)
        result = {doc["platform"]: doc["ports"] async for doc in cursor}
        return result
