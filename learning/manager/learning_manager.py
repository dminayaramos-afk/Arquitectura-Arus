from __future__ import annotations

from learning.domain.knowledge import KnowledgeItem
from learning.domain.repository import KnowledgeRepository
from learning.domain.exceptions import (
    DuplicateKnowledgeError,
    KnowledgeNotFoundError,
)


class LearningManager:
    """
    Núcleo del sistema de aprendizaje de ARUS.
    Todo el conocimiento entra por este gestor.
    """

    def __init__(self, repository: KnowledgeRepository):
        self.repository = repository

    def learn(self, item: KnowledgeItem) -> KnowledgeItem:
        if self.repository.exists(item.id):
            raise DuplicateKnowledgeError(
                f"Knowledge '{item.id}' ya existe."
            )

        self.repository.save(item)
        return item

    def remember(self, item_id: str) -> KnowledgeItem:
        item = self.repository.get(item_id)

        if item is None:
            raise KnowledgeNotFoundError(item_id)

        return item

    def reinforce(self, item_id: str, amount: float = 0.10) -> KnowledgeItem:
        item = self.remember(item_id)
        item.reinforce(amount)
        self.repository.update(item)
        return item

    def weaken(self, item_id: str, amount: float = 0.10) -> KnowledgeItem:
        item = self.remember(item_id)
        item.weaken(amount)
        self.repository.update(item)
        return item

    def forget(self, item_id: str) -> bool:
        if not self.repository.exists(item_id):
            return False

        return self.repository.delete(item_id)

    def search(self, query: str):
        return self.repository.search(query)

    def list(self):
        return self.repository.list()

    def clear(self):
        self.repository.clear()
