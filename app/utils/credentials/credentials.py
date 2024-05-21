from registrable import Registrable
from abc import ABC, abstractmethod

@abstractmethod
class Credentials(Registrable, ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @staticmethod
    def get_credentials():
        raise NotImplementedError("get_credentials method not implemented")
