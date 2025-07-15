import logging

from src.core.ports.normalizer import Normalizer
from src.core.ports.repositories import HostRawDataRepository, HostNormalizedDataRepository

logger = logging.getLogger(__name__)

class NormalizationService:
    def __init__(
            self,
            source_collection: str,
            target_collection: str,
            normalizer: Normalizer,
            raw_repository: HostRawDataRepository,
            normal_repository: HostNormalizedDataRepository,
    ):
        self.normalizer = normalizer
        self.raw_repository = raw_repository
        self.normal_repository = normal_repository
        self.source_collection = source_collection
        self.target_collection = target_collection

    async def normalize(self):
        async for raw_data_batch in self.raw_repository.get_raw_data(self.source_collection):
            normalized_data = [self.normalizer.normalize(raw_data) for raw_data in raw_data_batch]
            logger.info(f'Normalized {len(normalized_data)} docs')
            await self.normal_repository.save_normalized_data(self.target_collection, normalized_data)
