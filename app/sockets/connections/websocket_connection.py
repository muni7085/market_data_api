from abc import ABC, abstractmethod
from typing import Dict

from omegaconf import DictConfig
from registrable import Registrable

from app.sockets.twisted_socket import MarketDatasetTwistedSocket


class WebsocketConnection(ABC, Registrable):
    """
    This is the base class for all the websocket connections. It provides the interface
    for the websocket connections to implement. The websocket connections are responsible
    for creating a connection to the respective websocket servers and subscribing to the
    required tokens to get the live data for the tokens from server. The subclasses of this
    class should implement the `get_tokens` method to return the tokens for the respective
    exchange and instrument type. The subclasses should also has a class method `from_cfg`
    to create the object from the configuration to abstract complex object creation logic.

    Attributes
    ----------
    websocket: ``MarketDatasetTwistedSocket``
        The websocket object to connect to the respective websocket
    """

    def __init__(self, websocket: MarketDatasetTwistedSocket):
        self.websocket = websocket

    @abstractmethod
    def get_tokens(self, cfg: DictConfig) -> Dict[str, str]:
        """
        This method returns the tokens for the equity stocks based on the exchange
        and instrument type.

        Returns
        -------
        ``Dict[str, str]``
            A dictionary containing the tokens as keys and the symbols as values.
            Eg: {"256265": "INFY"}

        """
        pass

    @classmethod
    def from_cfg(cls, cfg: DictConfig) -> "WebsocketConnection":
        pass
