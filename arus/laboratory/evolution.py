"""
ARUS
Evolution Cycle
FASE 15
"""


class EvolutionCycle:


    def __init__(
        self,
        agent_manager,
        experiment_manager
    ):

        self.agents = agent_manager

        self.experiments = experiment_manager



    def execute(
        self,
        agent_name,
        experiment_name
    ):

        agent = self.agents.get(
            agent_name
        )

        experiment = self.experiments.get(
            experiment_name
        )


        agent.start()

        experiment.start()


        agent.work(
            "Ejecutando evolución supervisada"
        )


        experiment.complete(
            {
                "agent":agent.name,
                "evolution":"success"
            }
        )


        self.experiments.repository.save(
            experiment
        )


        self.agents.repository.save(
            agent
        )


        return {

            "agent":agent.info(),

            "experiment":experiment.info()

        }
