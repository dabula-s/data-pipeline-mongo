from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterable

from bson import ObjectId

from src.core.entities import HostNormalizedData, HostRawData, HostUnmergedDataGroup


class HostRawDataRepository(ABC):
    @abstractmethod
    async def save_raw_data(self, collection: str, documents: Iterable[HostRawData]) -> None:
        ...

    @abstractmethod
    async def get_raw_data(self, collection: str, batch_size: int = 10) -> AsyncIterator[list[HostRawData]]:
        ...


class HostNormalizedDataRepository(ABC):
    @abstractmethod
    async def save_normalized_data(self, collection: str, documents: Iterable[HostNormalizedData]) -> None:
        ...

    @abstractmethod
    async def get_normalized_data(self, collection: str, batch_size: int = 10) -> AsyncIterator[
        list[HostNormalizedData]]:
        ...

    @abstractmethod
    async def delete_normalized_data_by_ids(self, collection: str, ids: list[str | ObjectId]) -> None:
        ...

    @abstractmethod
    async def get_unmerged_docs_groups(self, collection, batch_size: int = 1) -> AsyncIterator[
        list[HostUnmergedDataGroup]]:
        ...

    @abstractmethod
    async def get_os_distribution(self, collection: str) -> dict[str, int]:
        ...

    @abstractmethod
    async def get_old_vs_new_hosts(self, collection: str, days_threshold: int = 30) -> dict[str, int]:
        ...

    @abstractmethod
    async def get_open_ports_distribution(self, collection: str) -> dict[int, int]:
        ...

    @abstractmethod
    async def get_open_ports_by_platform_distribution(self, collection: str, ports_list: list[int]) -> dict[
        str, dict[int, int]]:
        ...
