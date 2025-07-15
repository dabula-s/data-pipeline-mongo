from abc import ABC, abstractmethod

from src.core.entities import HostRawData, HostNormalizedData


class Normalizer(ABC):
    @abstractmethod
    def normalize(self, data: HostRawData) -> HostNormalizedData:
        ...
