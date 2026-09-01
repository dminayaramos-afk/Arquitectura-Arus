
"""
ARUS
Laboratory Runtime States
"""

from enum import Enum


class RuntimeState(Enum):

    CREATED = "created"

    STARTING = "starting"

    RUNNING = "running"

    PAUSED = "paused"

    STOPPING = "stopping"

    STOPPED = "stopped"

    ERROR = "error"
