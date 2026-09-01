from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4

from .enums import KnowledgeType, KnowledgeSource


@dataclass(slots=True)
class KnowledgeItem:
    id: str = field(default_factory=lambda: str(uuid4()))

    type: KnowledgeType = KnowledgeType.LEARNED
    source: KnowledgeSource = KnowledgeSource.SYSTEM

    title: str = ""
    content: str = ""

    confidence: float = 0.50
    version: int = 1

    tags: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def reinforce(self, amount: float = 0.10) -> None:
        self.confidence = min(1.0, self.confidence + amount)
        self.version += 1
        self.updated_at = datetime.now(UTC)

    def weaken(self, amount: float = 0.10) -> None:
        self.confidence = max(0.0, self.confidence - amount)
        self.version += 1
        self.updated_at = datetime.now(UTC)
