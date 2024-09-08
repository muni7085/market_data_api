from abc import ABC, abstractmethod

from registrable import Registrable


@abstractmethod
class Credentials(Registrable, ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @staticmethod
    def get_credentials():
        raise NotImplementedError("get_credentials method not implemented")
