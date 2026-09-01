
"""
ARUS
Experiment Model
"""

from datetime import datetime
import uuid

from .status import ExperimentStatus


class Experiment:


    def __init__(
        self,
        name,
        description=""
    ):

        self.id = str(uuid.uuid4())

        self.name = name

        self.description = description

        self.status = ExperimentStatus.CREATED

        self.created_at = datetime.now()

        self.started_at = None

        self.finished_at = None

        self.results = {}

        self.metadata = {}



    def start(self):

        self.status = ExperimentStatus.RUNNING

        self.started_at = datetime.now()



    def complete(
        self,
        results=None
    ):

        self.status = ExperimentStatus.COMPLETED

        self.finished_at = datetime.now()

        if results:

            self.results = results



    def fail(self):

        self.status = ExperimentStatus.FAILED

        self.finished_at = datetime.now()



    def info(self):

        return {

            "id": self.id,

            "name": self.name,

            "description": self.description,

            "status": self.status.value,

            "results": self.results,

            "metadata": self.metadata

        }
