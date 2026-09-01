from __future__ import annotations

from learning.domain.knowledge import KnowledgeItem
from learning.domain.repository import KnowledgeRepository


class InMemoryKnowledgeRepository(KnowledgeRepository):
    """
    Repositorio base en memoria.
    Será sustituido posteriormente por SQLite.
    """

    def __init__(self):
        self._data: dict[str, KnowledgeItem] = {}

    def save(self, item: KnowledgeItem) -> None:
        self._data[item.id] = item

    def update(self, item: KnowledgeItem) -> None:
        self._data[item.id] = item

    def get(self, item_id: str) -> KnowledgeItem | None:
        return self._data.get(item_id)

    def delete(self, item_id: str) -> bool:
        return self._data.pop(item_id, None) is not None

    def list(self) -> list[KnowledgeItem]:
        return list(self._data.values())

    def search(self, query: str) -> list[KnowledgeItem]:
        query = query.lower()

        return [
            item
            for item in self._data.values()
            if query in item.title.lower()
            or query in item.content.lower()
            or any(query in tag.lower() for tag in item.tags)
        ]

    def exists(self, item_id: str) -> bool:
        return item_id in self._data

    def clear(self) -> None:
        self._data.clear()
