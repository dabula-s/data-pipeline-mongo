import logging
from abc import ABC
from typing import AsyncGenerator

from aiohttp import ClientResponse, ClientSession, ClientError, ContentTypeError
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.settings import API_REQUESTS_RETRY_LIMIT

logger = logging.getLogger(__name__)


class APIClientConfig(ABC, BaseModel):
    slug: str
    api_token: str
    limit: int = Field(default=1, ge=1)
    offset: int = Field(default=0, ge=0)


class APIClient(ABC):
    slug: str
    endpoint_url: str
    method: str

    def __init__(self, config: APIClientConfig):
        if self.slug != config.slug:
            raise ValueError(f'Incorrect config for api client {self.__class__.__name__}. '
                             f'Slug {self.slug} does not match config slug {config.slug}.')
        self.config = config

    async def fetch_hosts(self, batch_size: int = 10) -> AsyncGenerator[list[dict], None]:
        limit = self.config.limit
        offset = self.config.offset
        batch = []
        async with ClientSession() as session:
            while content := await self.get_content(session, limit, offset):
                batch.extend(content)
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
                if len(content) < limit:
                    yield batch
                    logger.debug(f'Duw to api limitation for {self.slug} all possible data was fetched.')
                    break
                offset += limit
            yield batch

    async def get_content(self, session, limit: int, offset: int) -> list[dict] | None:
        response = await self.make_request(session, limit, offset)
        if response.status == 500 and await response.text() == 'Error invalid skip/limit combo (>number of hosts)':
            return []
        return await self.parse_response(response)

    @retry(
        stop=stop_after_attempt(API_REQUESTS_RETRY_LIMIT),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(ClientError)
    )
    async def make_request(self, session, limit: int, offset: int) -> ClientResponse:
        try:
            response = await session.request(
                method=self.method,
                url=self.endpoint_url,
                params={'limit': limit, 'skip': offset},
                headers={'Token': self.config.api_token},
            )
            return response
        except ClientError as e:
            logger.error(f'Error while fetching data from {self.endpoint_url}: {e}')
            raise

    async def parse_response(self, response: ClientResponse) -> list[dict]:
        try:
            return await response.json()
        except ContentTypeError as e:
            logger.error(f'Error while parsing response from {self.endpoint_url}: {e}')
            raise
