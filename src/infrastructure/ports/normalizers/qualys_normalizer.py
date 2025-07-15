from typing import Any

from src.core.entities import HostNormalizedData, HostRawData, OpenPort, Software
from src.core.ports.normalizer import Normalizer
from src.infrastructure.utils import dig


class QualysNormalizer(Normalizer):
    def normalize(self, data: HostRawData) -> HostNormalizedData:
        host_raw = data.data
        open_ports = dig(host_raw, 'openPort', 'list')
        software = dig(host_raw, 'software', 'list')
        vulnerabilities = dig(host_raw, 'vuln', 'list')
        source_info_list = dig(host_raw, 'sourceInfo', 'list')
        return HostNormalizedData(**dict(
            hostname=self._extract_value_from_source_info(source_info_list, 'localHostname'),
            local_ip=self._extract_value_from_source_info(source_info_list, 'privateIpAddress'),
            external_ip=self._extract_value_from_source_info(source_info_list, 'publicIpAddress'),
            mac_address=self._extract_value_from_source_info(source_info_list, 'macAddress'),
            provider=dig(host_raw, 'cloudProvider'),
            os_version=dig(host_raw, 'os'),
            platform=dig(host_raw, 'agentInfo', 'platform'),
            open_ports_count=len(open_ports) if open_ports else None,
            open_ports=[OpenPort(service_name=port_info.get('serviceName'), **port_info)
                        for port_info in self._extract_open_ports(open_ports)],
            software=[Software(**software_info) for software_info in self._extract_software(software)],
            vuln_count=len(vulnerabilities) if vulnerabilities else None,
            sources=[data.source],
        ))

    def _extract_open_ports(self, data: list[dict]) -> list[dict[str, Any]]:
        open_ports = []
        for host_asset_open_port in data:
            if (port_info := host_asset_open_port.get('HostAssetOpenPort', None)) and isinstance(port_info, dict):
                open_ports.append(port_info)
        return open_ports

    def _extract_software(self, data: list[dict]) -> list[dict[str, Any]]:
        software = []
        for host_asset_software in data:
            if ((software_info := host_asset_software.get('HostAssetSoftware', None))
                    and isinstance(software_info, dict)):
                software.append(software_info)
        return software

    def _extract_value_from_source_info(self, source_info_list: list[dict[str, Any]], target_key: str) -> str | None:
        for dictionary in source_info_list:
            for key, value in dictionary.items():
                if isinstance(value, dict) and target_key in value:
                    return value[target_key]

        return None
