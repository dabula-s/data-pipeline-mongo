import logging

from src.core.ports.merger import Merger
from src.core.ports.repositories import HostNormalizedDataRepository

logger = logging.getLogger(__name__)


class DeduplicationService:
    def __init__(
            self,
            collection: str,
            normal_repository: HostNormalizedDataRepository,
            merger: Merger,
    ):
        self.collection = collection
        self.normal_repository = normal_repository
        self.merger = merger

    async def deduplicate(self, batch_size: int = 10):
        logger.info(f'Deduplicating {self.collection}')
        async for groups_batch in self.normal_repository.get_unmerged_docs_groups(
                collection=self.collection,
                batch_size=batch_size,
        ):
            for group in groups_batch:
                if len(group.group_docs) == 1:
                    continue
                merged_doc = self.merger.merge(group)
                await self.normal_repository.delete_normalized_data_by_ids(
                    collection=self.collection,
                    ids=[doc.id for doc in group.group_docs],
                )
                await self.normal_repository.save_normalized_data(self.collection, [merged_doc])
