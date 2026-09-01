"""
ARUS
Agent Response
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class AgentResponse:

    success: bool

    answer: str = ""

    data: dict = field(default_factory=dict)

    errors: list = field(default_factory=list)

    metadata: dict = field(default_factory=dict)
