"""
ARUS
Command Base
"""

from abc import ABC, abstractmethod


class Command(ABC):

    name = "base"


    @abstractmethod
    def execute(
        self,
        args
    ) -> str:
        pass
