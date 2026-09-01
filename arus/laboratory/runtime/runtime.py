
"""
ARUS
Laboratory Runtime Engine
"""

from arus.laboratory.runtime.state import RuntimeState
from arus.laboratory.runtime.session import RuntimeSession



class LaboratoryRuntime:


    def __init__(
        self,
        laboratory
    ):

        self.laboratory = laboratory

        self.state = RuntimeState.CREATED

        self.session = None



    def start(self):

        self.state = RuntimeState.STARTING


        self.session = RuntimeSession(
            self.laboratory.name
        )


        self.state = RuntimeState.RUNNING


        return self.session



    def pause(self):

        if self.state == RuntimeState.RUNNING:

            self.state = RuntimeState.PAUSED



    def resume(self):

        if self.state == RuntimeState.PAUSED:

            self.state = RuntimeState.RUNNING



    def stop(self):

        self.state = RuntimeState.STOPPING


        if self.session:

            self.session.close()


        self.state = RuntimeState.STOPPED



    def info(self):

        return {

            "laboratory":
                self.laboratory.name,

            "state":
                self.state.value,

            "session":
                (
                    self.session.info()
                    if self.session
                    else None
                )

        }
