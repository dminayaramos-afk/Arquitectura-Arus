"""
ARUS
Laboratory Repository Interface
"""

from abc import ABC, abstractmethod


class LaboratoryRepository(ABC):

    @abstractmethod
    def save(self, laboratory):
        pass

    @abstractmethod
    def get(self, name):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def exists(self, name):
        pass

    @abstractmethod
    def delete(self, name):
        pass

    @abstractmethod
    def load(self, name, laboratory_class):
        pass
