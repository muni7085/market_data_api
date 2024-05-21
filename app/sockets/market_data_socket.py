from registrable import Registrable
from abc import ABC, abstractmethod


class MarketDataSocket(ABC, Registrable):
    def __init__(self, auth_token: str):
        self._auth_token = auth_token

    @abstractmethod
    def connect(self):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def on_message(self, ws, message):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def on_error(self, ws, error):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def on_close(self, ws):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def on_open(self, ws):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def subscribe(self, ws):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def unsubscribe(self, ws):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def decode_data(self, data):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def close(self):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def on_ping(self, ws, message):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def on_pong(self, ws, message):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def on_data(self, data):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def initialize_socket(self):
        raise NotImplementedError("Method not implemented")
