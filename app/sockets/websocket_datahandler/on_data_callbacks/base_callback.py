from abc import ABC, abstractmethod
from registrable import Registrable


class BaseCallback(ABC, Registrable):
    @abstractmethod
    def __call__(self, data):
        raise NotImplementedError

    @classmethod
    def from_cfg(cls, cfg):
        raise NotImplementedError
