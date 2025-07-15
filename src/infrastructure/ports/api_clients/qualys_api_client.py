from src.core.ports.api_client import APIClient


class QualysAPIClient(APIClient):
    slug = 'qualys'
    endpoint_url = 'https://api.recruiting.app.silk.security/api/qualys/hosts/get'
    method = 'POST'
