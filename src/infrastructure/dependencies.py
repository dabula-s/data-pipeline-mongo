import os

from src.core.ports.api_client import APIClientConfig
from src.infrastructure.db.mongo.client import get_mongo_client
from src.infrastructure.db.mongo.repositories import MongoHostRawDataRepository, MongoHostNormalizedDataRepository
from src.infrastructure.ports.api_clients.crowdstrike_api_client import CrowdstrikeAPIClient
from src.infrastructure.ports.api_clients.qualys_api_client import QualysAPIClient
from src.infrastructure.ports.mergers.priority_merger import PrioritySourceMerger
from src.infrastructure.ports.normalizers.crowdstrike_normalizer import CrowdstrikeNormalizer
from src.infrastructure.ports.normalizers.qualys_normalizer import QualysNormalizer
from src.settings import PIPELINE_CONFIG

SOURCES_API_CLIENTS = {
    'qualys': QualysAPIClient,
    'crowdstrike': CrowdstrikeAPIClient,
}

NORMALIZERS = {
    'qualys': QualysNormalizer(),
    'crowdstrike': CrowdstrikeNormalizer(),
}


def build_fetching_step_params() -> list[dict]:
    fetching_process_params = []
    for source_slug, source_config in PIPELINE_CONFIG['fetching']['sources'].items():
        api_config = {
            'slug': source_slug,
            'api_token': os.getenv(source_config['api_token_env']),
            'offset': source_config['offset'],
            'limit': source_config['limit'],
        }
        fetching_process_params.append({
            'source': source_slug,
            'collection': source_config['target_collection'],
            'api_client': SOURCES_API_CLIENTS[source_slug](config=APIClientConfig(**api_config)),
            'repository': MongoHostRawDataRepository(client=get_mongo_client()),
        })
    return fetching_process_params


def build_normalization_step_params() -> list[dict]:
    params = []
    for source_slug, source_config in PIPELINE_CONFIG['normalization']['sources'].items():
        params.append({
            'source_collection': source_config['source_collection'],
            'target_collection': source_config['target_collection'],
            'normalizer': NORMALIZERS[source_slug],
            'raw_repository': MongoHostRawDataRepository(client=get_mongo_client()),
            'normal_repository': MongoHostNormalizedDataRepository(client=get_mongo_client()),
        })
    return params


def build_deduplication_step_params() -> list[dict]:
    params = []
    for source_slug, source_config in PIPELINE_CONFIG['sources'].items():
        params.append({
            'source_collection': source_config['target_collection'],
            'target_collection': source_config['target_collection'],
            'normal_repository': MongoHostNormalizedDataRepository(client=get_mongo_client()),
            'merger': PrioritySourceMerger(source_priorities=PIPELINE_CONFIG['deduplication']['source_priorities']),
        })

    return params
