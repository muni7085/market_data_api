from abc import ABC, abstractmethod
from typing import Dict

from registrable import Registrable

from app.sockets.twisted_socket import MarketDatasetTwistedSocket


class WebsocketConnection(ABC, Registrable):
    def __init__(self, websocket: MarketDatasetTwistedSocket):
        self.websocket = websocket
    
    
    @abstractmethod
    def get_equity_stock_tokens(exchange: str = None, instrument_type: str = None, **kwargs)->Dict[str, str]:
       raise NotImplementedError
        
    
    @classmethod
    def from_cfg(cls, cfg):
        pass