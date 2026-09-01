"""
ARUS
Virtual Laboratory
Laboratory Status
"""

from enum import Enum


class LaboratoryStatus(str, Enum):
    """
    Estados posibles de un laboratorio.
    """

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
    ARCHIVED = "archived"
    DELETED = "deleted"

    @property
    def is_active(self) -> bool:
        """
        Indica si el laboratorio está operativo.
        """
        return self in (
            LaboratoryStatus.READY,
            LaboratoryStatus.RUNNING,
            LaboratoryStatus.PAUSED,
        )

    @property
    def is_finished(self) -> bool:
        """
        Indica si el laboratorio ya terminó.
        """
        return self in (
            LaboratoryStatus.FINISHED,
            LaboratoryStatus.ARCHIVED,
            LaboratoryStatus.DELETED,
        )

    def __str__(self) -> str:
        return self.value

