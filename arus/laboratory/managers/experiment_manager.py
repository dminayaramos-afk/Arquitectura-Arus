
"""
ARUS
Experiment Manager
"""

from arus.laboratory.experiments import Experiment
from arus.laboratory.repositories import ExperimentRepository


class ExperimentManager:


    def __init__(self):

        self._experiments = {}

        self.repository = ExperimentRepository()



    def create(
        self,
        name,
        description=""
    ):

        experiment = Experiment(
            name,
            description
        )

        self._experiments[name] = experiment

        self.repository.save(experiment)

        return experiment



    def get(
        self,
        name
    ):

        return self._experiments.get(name)



    def delete(
        self,
        name
    ):

        if name in self._experiments:

            del self._experiments[name]



    def list(self):

        self.repository.connection.commit()

        return list(
            self._experiments.values()
        )



    def count(self):

        return len(
            self._experiments
        )
