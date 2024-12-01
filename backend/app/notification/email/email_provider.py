from app.notification.provider import NotificationProvider
from abc import abstractmethod

class EmailProvider(NotificationProvider):
    @abstractmethod
    def send_notification(self, code:str, recipient_email:str) -> None:
        raise NotImplementedError("EmailProvider is an abstract class and cannot be instantiated directly.")
    