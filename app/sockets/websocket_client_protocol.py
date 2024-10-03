import time
from pathlib import Path

from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.websocket.types import ConnectionResponse

from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


class MarketDataWebScoketClientProtocol(WebSocketClientProtocol):
    """
    This class is a subclass of the `WebSocketClientProtocol` class from the `autobahn` library.
    It is used to create a WebSocket client protocol that can be used to connect to a WebSocket server
    and send and receive messages over the WebSocket connection.

    Attributes
    ----------
    PING_INTERVAL: ``float``
        The interval at which the client sends ping messages to the server to keep the connection alive
    KEEPALIVE_INTERVAL: ``float``
        The interval at which the client checks if the server is sending pong messages to keep the connection alive
    _last_pong_time: ``float``
        The timestamp of the last pong message received from the server
    _last_ping_time: ``float``
        The timestamp of the last ping message sent to the server
    """

    PING_INTERVAL = 2.5
    KEEPALIVE_INTERVAL = 5

    _next_ping = None
    _next_pong_check = None
    _last_pong_time = None
    _last_ping_time = None

    def __init__(self, *args, **kwargs):
        super(MarketDataWebScoketClientProtocol, self).__init__(*args, **kwargs)

    def onConnect(self, response: ConnectionResponse):
        """
        This callback is triggered immediately after the WebSocket opening handshake is completed
        and a new WebSocket connection is established between the client and the server

        Parameters
        ----------
        response: ``ConnectionResponse``
            A ConnectionResponse object that contains information about the connection, including:
            - The IP address of the server (`response.peer`)
            - Response headers received from the server
            - WebSocket protocol details and more
        """
        if self.factory.debug:
            logger.debug(f"Connected to {response.peer} with {response.protocol}")

        self.factory.ws = self

        if self.factory.on_connect:
            self.factory.on_connect(self, response)

        self.factory.resetDelay()

    def onOpen(self):
        """
        This callback is triggered when the WebSocket connection has been established
        and is open for sending and receiving messages
        """
        self._loop_ping()
        self._loop_pong_check()

        if self.factory.debug:
            logger.debug(f"Connection Opened")

        if self.factory.on_open:
            self.factory.on_open(self)

    def onMessage(self, payload: bytes, isBinary: bool):
        """
        This callback is triggered when a WebSocket message is received from the server

        Parameters
        ----------
        payload: ``bytes``
            The message payload received from the server
        isBinary: ``bool``
            A boolean flag that indicates whether the message is binary or text
        """
        if self.factory.on_message:
            self.factory.on_message(self, payload, isBinary)

    def onClose(self, was_clean: bool, code: int, reason: str):
        """
        This callback is triggered when the WebSocket connection is closed

        Parameters
        ----------
        was_clean: ``bool``
            A boolean flag that indicates whether the connection was closed cleanly
            meaning that the closing handshake was completed successfully
        code: ``int``
            The close status code sent by the server
        reason: ``str``
            The reason for closing the connection sent by the server
        """
        if not was_clean:
            if self.factory.on_error:
                self.factory.on_error(self, code, reason)

        if self.factory.on_close:
            self.factory.on_close(self, code, reason)

        self._last_ping_time = None
        self._last_pong_time = None

        if self._next_ping:
            self._next_ping.cancel()

        if self._next_pong_check:
            self._next_pong_check.cancel()

    def onPing(self, payload: str):
        """
        This callback is triggered when a WebSocket ping message is received from the server.
        This method is used to respond to the ping message with a pong message and to keep
        the connection alive as long as the server is sending ping messages.

        Parameters
        ----------
        payload: ``str``
            The payload of the ping message received from the server
        """

        if self._last_ping_time and self.factory.debug:
            logger.debug(f"Last pong was received at {time.time-self._last_pong_time}")

        self._last_ping_time = time.time()

        if self.factory.debug:
            logger.debug(f"Received ping {payload}")

    def _loop_ping(self):
        """
        This method is used to send a ping message to the server at regular intervals
        to keep the connection alive.
        """
        if self.factory.debug:
            if self._last_ping_time:
                logger.debug(
                    f"Last ping was sent at {time.time()-self._last_ping_time}"
                )

        self._last_ping_time = time.time()
        self._next_ping = self.factory.reactor.callLater(
            self.PING_INTERVAL, self._loop_ping
        )

    def _loop_pong_check(self):
        """
        This method is used to check if the server is sending pong messages at regular intervals
        to keep the connection alive. If the server does not send a pong message within the
        specified interval, the connection is dropped and reconnected
        """
        if self._last_pong_time:
            last_pong_diff = time.time() - self._last_pong_time

            if last_pong_diff > (2 * self.PING_INTERVAL):
                if self.factory.debug:
                    logger.debug(
                        f"Last pong was received at {last_pong_diff}. So dropping the connection to reconnect"
                    )
                self.dropConnection(abort=True)

        self._next_pong_check = self.factory.reactor.callLater(
            self.KEEPALIVE_INTERVAL, self._loop_pong_check
        )
