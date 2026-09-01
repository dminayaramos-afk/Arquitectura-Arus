
"""
ARUS
Laboratory Agent
"""

import uuid
from datetime import datetime

from .status import AgentStatus


class Agent:


    def __init__(
        self,
        name,
        role=""
    ):

        self.id = str(uuid.uuid4())

        self.name = name

        self.role = role

        self.status = AgentStatus.CREATED

        self.created_at = datetime.now()

        self.tasks = []



    def start(self):

        self.status = AgentStatus.IDLE



    def work(self, task):

        self.status = AgentStatus.WORKING

        self.tasks.append(task)



    def stop(self):

        self.status = AgentStatus.STOPPED



    def info(self):

        return {

            "id": self.id,

            "name": self.name,

            "role": self.role,

            "status": self.status.value,

            "tasks": self.tasks

        }
