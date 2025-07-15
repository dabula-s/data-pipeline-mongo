import asyncio
import logging

import click

from src.infrastructure.db.mongo.client import get_mongo_client
from src.infrastructure.db.mongo.migrations import create_indexes as run_migrations
from src.settings import MONGODB_DATABASE

logger = logging.getLogger(__name__)


@click.group()
def database():
    pass


@database.command()
def drop_collections():
    async def run():
        mongo_client = get_mongo_client()
        db = mongo_client[MONGODB_DATABASE]
        drop_list = await db.list_collection_names()
        for collection in drop_list:
            logger.info(f'Dropping collection {collection}')
            await db.drop_collection(collection)

    asyncio.run(run())


@database.command()
def create_indexes():
    logger.info('Creating indexes')
    async def run():
        mongo_client = get_mongo_client()
        await run_migrations(client=mongo_client)

    asyncio.run(run())
