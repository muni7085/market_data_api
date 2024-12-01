from abc import ABC, abstractmethod

class NotificationProvider(ABC):
    @abstractmethod
    def send_notification(self, message: str, recipient: str) -> None:
        raise NotImplementedError("NotificationProvider is an abstract class and cannot be instantiated directly.")