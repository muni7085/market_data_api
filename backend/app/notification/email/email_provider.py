from omegaconf import DictConfig
from app.notification.provider import NotificationProvider
from abc import abstractmethod

@NotificationProvider.register("email_provider")
class EmailProvider(NotificationProvider):
    
    @abstractmethod
    def send_notification(self, code:str, recipient_email:str) -> None:
        raise NotImplementedError("EmailProvider is an abstract class and cannot be instantiated directly.")
    
    
    @classmethod
    @abstractmethod
    def from_cfg(cls, cfg: DictConfig) -> "EmailProvider":
        raise NotImplementedError("EmailProvider is an abstract class and cannot be instantiated directly.")