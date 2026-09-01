"""
ARUS
Message
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Message:

    sender: str

    receiver: str

    content: str

    created_at: datetime = field(
        default_factory=datetime.now
    )

    metadata: dict = field(
        default_factory=dict
    )
