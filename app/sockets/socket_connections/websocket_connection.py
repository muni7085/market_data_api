from registrable import Registrable
from abc import ABC, abstractmethod
from typing import Dict
from app.sockets.twisted_socket import MarketDatasetTwistedSocket

class WebsocketConnection(ABC, Registrable):
    def __init__(self, websocket):
        self.websocket = websocket
    
    
    @abstractmethod
    def get_equity_stock_tokens(symbol_type: str = None, exch_seg: str = None, **kwargs)->Dict[str, str]:
       raise NotImplementedError
        
    
    @classmethod
    def from_cfg(cls, cfg):
        pass