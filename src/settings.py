import json
import os


def __get_config(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f'Config file not found at {path}')
    with open(path, 'r') as f:
        return json.load(f)


LOGGING_CONFIG_PATH = os.environ.get('LOGGING_CONFIG_PATH', 'configs/logging_config.json')
LOGGING_CONFIG = __get_config(LOGGING_CONFIG_PATH)

MONGODB_USER = os.environ.get('MONGODB_USER', 'admin')
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', 'password')
MONGODB_HOST = os.environ.get('MONGODB_HOST', 'localhost')
MONGODB_PORT = os.environ.get('MONGODB_PORT', 27017)
MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE', 'main')
MONGODB_URL = f'mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}'

QUALYS_API_KEY = os.environ.get('QUALYS_API_KEY')
CROWDSTRIKE_API_KEY = os.environ.get('CROWDSTRIKE_API_KEY')

API_REQUESTS_RETRY_LIMIT = int(os.environ.get('API_REQUESTS_RETRY_LIMIT', 3))

PIPELINE_CONFIG_PATH = os.environ.get('PIPELINE_CONFIG_PATH', 'configs/pipeline_config.json')
PIPELINE_CONFIG = __get_config(PIPELINE_CONFIG_PATH)

PLOTS_SOURCE_COLLECTION = os.getenv('PLOTS_SOURCE_COLLECTION', 'normalized_data')
