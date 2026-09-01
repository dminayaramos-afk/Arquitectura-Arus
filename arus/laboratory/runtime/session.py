
"""
ARUS
Laboratory Runtime Session
"""

from datetime import datetime
import uuid


class RuntimeSession:


    def __init__(
        self,
        laboratory_name,
    ):

        self.id = str(uuid.uuid4())

        self.laboratory_name = laboratory_name

        self.started_at = datetime.now()

        self.finished_at = None


    def close(self):

        self.finished_at = datetime.now()


    def info(self):

        return {

            "id": self.id,

            "laboratory":
                self.laboratory_name,

            "started":
                self.started_at.isoformat(),

            "finished":
                (
                    self.finished_at.isoformat()
                    if self.finished_at
                    else None
                )

        }
