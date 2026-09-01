
"""
ARUS
Laboratory Runtime Manager
"""

from arus.laboratory.runtime import LaboratoryRuntime
from arus.laboratory.repositories import RuntimeRepository



class RuntimeManager:


    def __init__(self):

        self._runtimes = {}

        self.repository = RuntimeRepository()



    def start(
        self,
        laboratory
    ):

        if laboratory.name in self._runtimes:

            return self._runtimes[
                laboratory.name
            ]


        runtime = LaboratoryRuntime(
            laboratory
        )

        runtime.start()

        self.repository.save(runtime)


        self._runtimes[
            laboratory.name
        ] = runtime


        return runtime



    def get(
        self,
        laboratory_name
    ):

        return self._runtimes.get(
            laboratory_name
        )



    def exists(
        self,
        laboratory_name
    ):

        return laboratory_name in self._runtimes



    def stop(
        self,
        laboratory_name
    ):

        runtime = self.get(
            laboratory_name
        )


        if runtime:

            runtime.stop()

            self.repository.save(runtime)

            del self._runtimes[
                laboratory_name
            ]



    def list(self):

        return list(
            self._runtimes.values()
        )



    def clear(self):

        for runtime in self._runtimes.values():

            runtime.stop()

            self.repository.save(runtime)


        self._runtimes.clear()
