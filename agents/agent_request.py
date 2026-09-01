"""
ARUS
Agent Request
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class AgentRequest:

    message: str

    user: str = "user"

    context: dict = field(default_factory=dict)

    metadata: dict = field(default_factory=dict)
