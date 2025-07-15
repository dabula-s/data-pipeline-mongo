from abc import ABC

from src.core.entities import HostNormalizedData, HostUnmergedDataGroup


class Merger(ABC):
    def merge(self, group: HostUnmergedDataGroup) -> HostNormalizedData:
        raise NotImplementedError
