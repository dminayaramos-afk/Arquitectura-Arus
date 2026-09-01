from __future__ import annotations

from abc import ABC, abstractmethod

from .knowledge import KnowledgeItem


class KnowledgeRepository(ABC):
    """Contrato base para cualquier repositorio de conocimiento."""

    @abstractmethod
    def save(self, item: KnowledgeItem) -> None:
        pass

    @abstractmethod
    def update(self, item: KnowledgeItem) -> None:
        pass

    @abstractmethod
    def get(self, item_id: str) -> KnowledgeItem | None:
        pass

    @abstractmethod
    def delete(self, item_id: str) -> bool:
        pass

    @abstractmethod
    def list(self) -> list[KnowledgeItem]:
        pass

    @abstractmethod
    def search(self, query: str) -> list[KnowledgeItem]:
        pass

    @abstractmethod
    def exists(self, item_id: str) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
