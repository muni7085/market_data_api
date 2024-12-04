from abc import ABC, abstractmethod
from registrable import Registrable
from omegaconf import DictConfig

class NotificationProvider(ABC,Registrable):
    @abstractmethod
    def send_notification(self, message: str, recipient: str) -> None:
        raise NotImplementedError("NotificationProvider is an abstract class and cannot be instantiated directly.")
    
    @classmethod
    @abstractmethod
    def from_cfg(cls, cfg: DictConfig) -> "NotificationProvider":
        raise NotImplementedError("NotificationProvider is an abstract class and cannot be instantiated directly.")