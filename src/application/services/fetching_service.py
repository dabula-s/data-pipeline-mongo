import logging

from src.core.entities import HostRawData
from src.core.ports.api_client import APIClient
from src.core.ports.repositories import HostRawDataRepository

logger = logging.getLogger(__name__)


class FetchingService:
    def __init__(self, source: str, collection: str, repository: HostRawDataRepository, api_client: APIClient):
        self.source = source
        self.collection = collection
        self.repository = repository
        self.api_client = api_client

    async def fetch_data(self):
        async for hosts_raw_data in self.api_client.fetch_hosts():
            logger.info(f'Fetched {len(hosts_raw_data)} hosts from {self.api_client.slug}')
            documents = [HostRawData(source=self.source, data=data) for data in hosts_raw_data]
            await self.repository.save_raw_data(collection=self.collection, documents=documents)
