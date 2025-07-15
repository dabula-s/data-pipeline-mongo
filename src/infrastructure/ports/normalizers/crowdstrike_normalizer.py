from src.core.entities import HostNormalizedData, HostRawData
from src.core.ports.normalizer import Normalizer
from src.infrastructure.utils import dig


class CrowdstrikeNormalizer(Normalizer):
    def normalize(self, data: HostRawData) -> HostNormalizedData:
        host_raw = data.data
        return HostNormalizedData(**dict(
            hostname=dig(host_raw, 'hostname'),
            local_ip=dig(host_raw, 'local_ip'),
            external_ip=dig(host_raw, 'external_ip'),
            mac_address=self._normalize_mac_address(dig(host_raw, 'mac_address')),
            provider=dig(host_raw, 'service_provider'),
            os_version=dig(host_raw, 'os_version'),
            platform=dig(host_raw, 'platform_name'),
            first_seen_at=dig(host_raw, 'first_seen'),
            last_seen_at=dig(host_raw, 'last_seen'),
            sources=[data.source],
        ))

    def _normalize_mac_address(self, value: str) -> str | None:
        return value.replace('-', ':') if isinstance(value, str) else None

    def _normalize_provider(self, value: str) -> str:
        if isinstance(value, str) and value.startswith('AWS'):
            return 'AWS'
        return value
