from abc import ABC, abstractmethod

from registrable import Registrable


class DataSaver(ABC, Registrable):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def retrieve_and_save(self):
        pass

    @abstractmethod
    def from_cfg(cls, cfg) -> "DataSaver":
        pass
