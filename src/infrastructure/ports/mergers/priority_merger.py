import logging
from datetime import datetime

from src.core.entities import HostNormalizedData, HostUnmergedDataGroup
from src.core.ports.merger import Merger
from src.infrastructure.utils import dig

logger = logging.getLogger(__name__)


class PrioritySourceMerger(Merger):
    def __init__(self, source_priorities: dict):
        self.source_priorities = source_priorities

    def merge(self, group: HostUnmergedDataGroup) -> HostNormalizedData:
        logger.info(f'Merging group {group.group_id}, docs count: {len(group.group_docs)}')
        merged_doc = group.group_id
        merged_doc['sources'] = []
        ordered_docs = self.__order_docs(group.group_docs)
        for doc in ordered_docs:
            for key, value in doc.model_dump(exclude_unset=True).items():
                if key not in merged_doc and value:
                    merged_doc[key] = value
                    merged_doc['sources'].extend(doc.sources)
                    continue
        merged_doc['sources'] = list(set(merged_doc['sources']))
        result_doc = HostNormalizedData(**merged_doc)
        result_doc.first_seen_at = self.__merge_first_seen_at(docs=group.group_docs)
        result_doc.last_seen_at = self.__merge_last_seen_at(docs=group.group_docs)

        return result_doc

    def __order_docs(self, docs: list[HostNormalizedData]) -> list[HostNormalizedData]:
        return sorted(
            docs,
            key=lambda d: self.source_priorities.get(dig(d.sources, 0), 0),
            reverse=True,
        )

    def __merge_first_seen_at(self, docs: list[HostNormalizedData]) -> datetime | None:
        datetime_ordered = sorted([doc.first_seen_at for doc in docs if doc.first_seen_at])
        return datetime_ordered[0] if datetime_ordered else None

    def __merge_last_seen_at(self, docs: list[HostNormalizedData]) -> datetime | None:
        datetime_ordered = sorted([doc.last_seen_at for doc in docs if doc.last_seen_at], reverse=True)
        return datetime_ordered[0] if datetime_ordered else None
