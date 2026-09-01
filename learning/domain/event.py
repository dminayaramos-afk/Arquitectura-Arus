from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4

from .enums import KnowledgeSource


@dataclass(slots=True)
class LearningEvent:
    id: str = field(default_factory=lambda: str(uuid4()))
    source: KnowledgeSource = KnowledgeSource.SYSTEM
    event_type: str = ""
    payload: dict[str, object] = field(default_factory=dict)
    status: str = "pending"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def mark_processed(self) -> None:
        self.status = "processed"

    def mark_failed(self) -> None:
        self.status = "failed"
