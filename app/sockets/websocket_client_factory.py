import time
from pathlib import Path

from autobahn.twisted.websocket import WebSocketClientFactory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.tcp import Connector

from app.sockets.websocket_client_protocol import MarketDataWebScoketClientProtocol
from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


class MarketDataWebSocketClientFactory(
    WebSocketClientFactory, ReconnectingClientFactory
):
    """
    This class is used to create a WebSocket client factory that can be used to establish a connection
    to a WebSocket server and handle the connection lifecycle events such as connection failure, connection loss,
    reconnection, etc.

    Attributes
    ----------
    protocol: ``MarketDataWebScoketClientProtocol``
        The protocol class that is used to create a WebSocket client protocol
    maxDelay: ``int``
        The maximum delay (in seconds) between reconnection attempts
    max_retries: ``int``
        The maximum number of reconnection attempts before stopping the connection
    _last_connection_time: ``float``
        The timestamp of the last connection attempt
    """

    protocol = MarketDataWebScoketClientProtocol
    max_delay = 5
    max_retries = 10

    _last_connection_time = None

    def __init__(self, *args, **kwargs):

        self.debug = False
        self.ws = None
        self.on_connect = None
        self.on_open = None
        self.on_message = None
        self.error = None
        self.on_reconnect = None
        self.on_noreconnect = None
        self.on_close = None
        super(MarketDataWebSocketClientFactory, self).__init__(*args, **kwargs)

    def startedConnecting(self, connector: Connector):
        """
        This callback is triggered when the client starts connecting to the server

        Parameters
        ----------
        connector: ``Connector``
            The connector object that is used to establish a connection to the
            WebSocket server
        """
        if not self._last_connection_time and self.debug:
            logger.debug("Connection started")

        self._last_connection_time = time.time()

    def clientConnectionFailed(self, connector: Connector, reason: str):
        """
        This callback is triggered when the client fails to connect to the server

        Parameters
        ----------
        connector: ``Connector``
            The connector object that is used to establish a connection to the
            WebSocket server
        reason: ``str``
            The reason for the connection failure (e.g., "Connection refused")
        """
        if self.retries > 0:
            logger.error(f"Connection failed. Reason: {reason}")
            logger.info(
                f"Trying to reconnect in {int(round(self.delay))}. Retries left: {self.retries}"
            )

            if self.on_reconnect:
                self.on_reconnect(self.retries)

        self.retry(connector)
        self.send_noreconnect()

    def clientConnectionLost(self, connector: Connector, reason: str):
        """
        This callback is triggered when the client loses the connection to the server
        meaning that the connection was established but then lost for some reason

        Parameters
        ----------
        connector: ``Connector``
            The connector object that is used to establish a connection to the
            WebSocket server
        reason: ``str``
            The reason for the connection loss (e.g., "Connection lost")
        """
        if self.retries > 0:
            logger.error(f"Connection lost. Reason: {reason}")
            logger.info(
                f"Trying to reconnect in {int(round(self.delay))}. Retries left: {self.retries}"
            )

            if self.on_reconnect:
                self.on_reconnect(self.retries)

        self.retry(connector)
        self.send_noreconnect()

    def send_noreconnect(self):
        """
        This method is used to check if the maximum number of retries has been reached
        and if so, it stops the connection and calls the on_noreconnect callback
        """
        if self.max_retries and (self.retries > self.max_retries):
            if self.debug:
                logger.debug(
                    f"Max {self.max_retries} retries reached. Stopping the connection"
                )

                self.stop()

            if self.on_noreconnect:
                self.on_noreconnect()
