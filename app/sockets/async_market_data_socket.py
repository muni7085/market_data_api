from websockets.client import WebSocketClientProtocol
from abc import ABC, abstractmethod


class AsyncMarketDataSocket(ABC):
    def __init__(self, auth_token: str):
        self.__auth_token = auth_token

    @abstractmethod
    async def connect(self):
        raise NotImplementedError

    @abstractmethod
    def set_tokens(self, tokens: list):
        raise NotImplementedError

    @abstractmethod
    async def subscribe(self, ws: WebSocketClientProtocol):
        raise NotImplementedError

    @abstractmethod
    async def on_data(self):
        raise NotImplementedError

    @abstractmethod
    async def on_open(self,ws: WebSocketClientProtocol):
        raise NotImplementedError
