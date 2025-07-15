from src.core.ports.api_client import APIClient


class CrowdstrikeAPIClient(APIClient):
    slug = 'crowdstrike'
    endpoint_url = 'https://api.recruiting.app.silk.security/api/crowdstrike/hosts/get'
    method = 'POST'
