
"""
ARUS
Agent Status
"""

from enum import Enum


class AgentStatus(Enum):

    CREATED="created"

    IDLE="idle"

    WORKING="working"

    STOPPED="stopped"

    ERROR="error"
