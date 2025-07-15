from src.application.services.deduplication_service import DeduplicationService
from src.application.services.fetching_service import FetchingService
from src.application.services.normalization_service import NormalizationService
from src.infrastructure.db.mongo.client import get_mongo_client
from src.infrastructure.db.mongo.repositories import MongoHostNormalizedDataRepository
from src.infrastructure.dependencies import build_fetching_step_params, build_normalization_step_params
from src.infrastructure.ports.mergers.priority_merger import PrioritySourceMerger
from src.infrastructure.utils import run_parallel, run_via_asyncio
from src.settings import PIPELINE_CONFIG


def fetching_step():
    def run_fetching_process(source, collection, api_client, repository):
        async def run():
            fetching_service = FetchingService(
                source=source,
                collection=collection,
                api_client=api_client,
                repository=repository,
            )
            await fetching_service.fetch_data()

        run_via_asyncio(run())

    run_parallel(run_fetching_process, build_fetching_step_params())


def normalization_step():
    def run_normalization_process(source_collection, target_collection, normalizer, raw_repository, normal_repository):
        async def run():
            normalization_service = NormalizationService(
                source_collection=source_collection,
                target_collection=target_collection,
                normalizer=normalizer,
                raw_repository=raw_repository,
                normal_repository=normal_repository,
            )
            await normalization_service.normalize()

        run_via_asyncio(run())

    run_parallel(run_normalization_process, build_normalization_step_params())


def deduplication_step():
    async def run():
        normalized_data_repository = MongoHostNormalizedDataRepository(client=get_mongo_client())
        deduplication_service = DeduplicationService(
            collection=PIPELINE_CONFIG['deduplication']['collection'],
            normal_repository=normalized_data_repository,
            merger=PrioritySourceMerger(source_priorities=PIPELINE_CONFIG['deduplication']['source_priorities']),
        )
        await deduplication_service.deduplicate()

    run_via_asyncio(run())


if __name__ == "__main__":
    fetching_step()
    normalization_step()
    deduplication_step()
