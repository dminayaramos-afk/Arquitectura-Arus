
"""
ARUS
Experiment Status
"""

from enum import Enum


class ExperimentStatus(Enum):

    CREATED = "created"

    QUEUED = "queued"

    RUNNING = "running"

    PAUSED = "paused"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"
