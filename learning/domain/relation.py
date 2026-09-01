from dataclasses import dataclass, field
from uuid import uuid4

from .enums import RelationType


@dataclass(slots=True)
class KnowledgeRelation:
    id: str = field(default_factory=lambda: str(uuid4()))
    from_id: str = ""
    to_id: str = ""
    relation_type: RelationType = RelationType.RELATED_TO
    weight: float = 1.0

    def strengthen(self, amount: float = 0.1) -> None:
        self.weight = min(1.0, self.weight + amount)

    def weaken(self, amount: float = 0.1) -> None:
        self.weight = max(0.0, self.weight - amount)
