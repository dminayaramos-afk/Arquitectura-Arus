
"""
ARUS
Laboratory Ecosystem Controller
FASE 15 FINAL
"""

from arus.laboratory.managers import (
    LaboratoryManager,
    ExperimentManager,
    AgentManager,
)


class LaboratoryController:


    def __init__(self):

        self.laboratories = LaboratoryManager()

        self.experiments = ExperimentManager()

        self.agents = AgentManager()



    def create_lab(
        self,
        name,
        description=""
    ):

        return self.laboratories.create(
            name,
            description
        )



    def create_experiment(
        self,
        name,
        description=""
    ):

        return self.experiments.create(
            name,
            description
        )



    def create_agent(
        self,
        name,
        role=""
    ):

        return self.agents.create(
            name,
            role
        )



    def start_lab(
        self,
        name
    ):

        return self.laboratories.start_runtime(
            name
        )



    def info(self):

        return {

            "laboratories":
                len(
                    self.laboratories.list()
                ),

            "experiments":
                self.experiments.count(),

            "agents":
                self.agents.count()

        }
