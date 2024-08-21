import sys
import threading
from pathlib import Path
from twisted.internet import reactor, ssl
from twisted.python import log as twisted_log
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import connectWS
from app.sockets.websocket_client_factory import MarketDataWebSocketClientFactory

from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


class MarketDatasetTwistedSocket(ABC):
    WEBSOCKET_URL = None

    def __init__(
        self,
        max_retries: int = 5,
        reconnect: bool = True,
        ping_interval: int = 5,
        reconnect_max_tries: int = 5,
        reconnect_max_delay: int = 5,
        connection_timeout=5,
        debug: bool = False,
    ):
        self.ping_interval = ping_interval
        self.RESUBSCRIBE = False
        self.max_retries = max_retries
        self.reconnect_max_tries = reconnect_max_tries
        self.reconnect = reconnect
        self.reconnect_max_delay = reconnect_max_delay
        self.connection_timeout = connection_timeout
        self.debug = debug

        self._is_first_connect = True

        self.ws = None

        self.on_tick = None
        self.on_connect = None
        self.on_open = None
        self.on_message = None
        self.on_error = None
        self.on_close = None
        self.on_reconnect = None
        self.on_noreconnect = None

    @abstractmethod
    def set_tokens(self, tokens: List[Dict[str, int | Dict[str, str]]]):
        """
        Set the tokens to subscribe to the WebSocket connection

        """
        raise NotImplementedError

    def _create_connection(self, url, **kwargs):
        """
        This function creates a WebSocket client factory instance with the specified URL
        and options and sets the appropriate callbacks for the WebSocket connection

        Parameters
        ----------
        url: ``str``
            The URL of the WebSocket server
        kwargs: ``dict``
            Additional options to pass to the WebSocket client factory
        """
        self.factory = MarketDataWebSocketClientFactory(url, **kwargs)
        self.ws = self.factory.ws
        self.factory.debug = self.debug

        self.factory.on_connect = self._on_connect
        self.factory.on_open = self._on_open
        self.factory.on_message = self._on_message
        self.factory.on_error = self._on_error
        self.factory.on_close = self._on_close
        self.factory.on_reconnect = self._on_reconnect
        self.factory.on_noreconnect = self._on_noreconnect

        self.factory.maxDelay = self.reconnect_max_delay
        self.factory.maxRetries = self.reconnect_max_tries

    def connect(self, threaded=False, disable_ssl_verification=False, proxy=None):
        """
        This function establishes a WebSocket connection to the server with the specified URL.
        The connection can be run in a separate thread by setting the `threaded` parameter to True

        Parameters
        ----------
        threaded: ``bool``
            A boolean flag that indicates whether to run the connection in a separate thread
        disable_ssl_verification: ``bool``
            A boolean flag that indicates whether to disable SSL verification
        proxy: ``str``
            The proxy URL to use for the WebSocket connection
        """

        # Check if the WebSocket URL and headers are set by the implementation class
        assert self.WEBSOCKET_URL, "WEBSOCKET_URL is not set"
        assert self.headers, "Headers are not set"

        self._create_connection(self.WEBSOCKET_URL, proxy=proxy, headers=self.headers)
        context_factory = None

        if self.factory.isSecure and not disable_ssl_verification:
            context_factory = ssl.ClientContextFactory()

        connectWS(
            self.factory,
            contextFactory=context_factory,
            timeout=self.connection_timeout,
        )

        if self.debug:
            twisted_log.startLogging(sys.stdout)

        opts = {}
        if not reactor.running:
            if threaded:
                opts["installSignalHandlers"] = False
                self.websocket_thread = threading.Thread(target=reactor.run, kwargs=opts)
                self.websocket_thread.deamon = True
                self.websocket_thread.start()
            else:
                reactor.run(**opts)

    def is_connected(self):
        """
        This function checks if the WebSocket connection is open or not
        """
        if self.ws and self.ws.state == self.ws.STATE_OPEN:
            return True

        return False

    def _close(self, code: Optional[int] = None, reason: Optional[str] = None):
        """
        This function closes the WebSocket connection with the specified code and reason
        It was called by the close and stop_retry functions

        Parameters
        ----------
        code: ``int``
            The close status code to send to the server
        reason: ``str``
            The reason for closing the connection
        """
        if self.ws:
            self.ws.sendClose(code, reason)
            self.ws = None

    def close(self, code: Optional[int] = None, reason: Optional[str] = None):
        """
        This function closes the WebSocket connection with the specified code and reason

        Parameters
        ----------
        code: ``int``
            The close status code to send to the server
        reason: ``str``
            The reason for closing the connection
        """
        self.stop_retry()
        self._close(code, reason)

    def stop(self):
        """
        This function stops the reactor and closes the WebSocket connection
        """
        reactor.stop()

    def stop_retry(self):
        """
        This function stops the retry mechanism for the WebSocket connection
        so that the connection is not re-established after it is closed
        """
        if self.factory:
            self.factory.stopTrying()

    @abstractmethod
    def subscribe(self, tokens: List[Any]):
        """
        Subscribe to the specified tokens on the WebSocket connection.
        After subscribing, the WebSocket connection will receive data for the specified tokens.

        Parameters
        ----------
        tokens: ``List[Any]``
            A list of tokens to subscribe to the WebSocket connection
        """
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, tokens: List[Any]):
        """
        Unsubscribe from the specified tokens on the WebSocket connection.
        After unsubscribing, the WebSocket connection will no longer receive data for the specified tokens.

        Parameters
        ----------
        tokens: ``List[Any]``
            A list of tokens to unsubscribe from the WebSocket connection
        """
        raise NotImplementedError

    @abstractmethod
    def resubscribe(self):
        """
        Resubscribe to the tokens on the WebSocket connection.
        This function is called when the connection is re-established after a disconnection.
        """
        raise NotImplementedError

    def _on_connect(self, ws: WebSocketClientProtocol, response):
        self.ws = ws

        if self.debug:
            logger.debug("Connected to the server")

        if self.on_connect:
            self.on_connect(ws, response)

    def _on_close(self, ws: WebSocketClientProtocol, code: int, reason: str):
        """
        This function is called when the WebSocket connection is closed

        Parameters
        ----------
        ws: ``WebSocketClientProtocol``
            The WebSocket client protocol object
        code: ``int``
            The close status code sent by the server
        reason: ``str``
            The reason for closing the connection sent by the server
        """

        if self.debug:
            logger.debug(f"Connection closed. Code: {code}, Reason: {reason}")

        if self.on_close:
            self.on_close(ws, code, reason)

    def _on_error(self, ws: WebSocketClientProtocol, code: int, reason: str):
        """
        This function is called when an error occurs in the WebSocket connection

        Parameters
        ----------
        ws: ``WebSocketClientProtocol``
            The WebSocket client protocol object
        code: ``int``
            The close status code sent by the server
        reason: ``str``
            The reason for closing the connection sent by the server
        """
        if self.debug:
            logger.debug(f"Error. Code: {code}, Reason: {reason}")

        if self.on_error:
            self.on_error(ws, code, reason)

    @abstractmethod
    def _on_message(self, ws: WebSocketClientProtocol, payload: bytes, is_binary: bool):
        """
        This function is called when a message is received from the WebSocket server

        Parameters
        ----------
        ws: ``WebSocketClientProtocol``
            The WebSocket client protocol object
        payload: ``bytes``
            The message payload received from the server
        is_binary: ``bool``
            A boolean flag that indicates whether the message is binary or text
        """
        raise NotImplementedError

    def _on_open(self, ws: WebSocketClientProtocol):
        """
        This function is called when the WebSocket connection is opened.
        It sends a ping message to the server to keep the connection alive.
        When the connection is open, it also resubscribes to the tokens if it is not the first connection.
        If it is the first connection, it subscribes to the tokens.

        Parameters
        ----------
        ws: ``WebSocketClientProtocol``
            The WebSocket client protocol object
        """
        if self.debug:
            logger.info(f"on open : {ws.state}")

        if not self._is_first_connect:
            self.resubscribe()
        else:
            self.subscribe(self._tokens)

        self._is_first_connect = False

    def _on_reconnect(self, retries: int):
        """
        This function is called when the WebSocket connection is re-established after a
        disconnection to reconnect to the server

        Parameters
        ----------
        retries: ``int``
            The number of retries left for reconnection
        """
        if self.debug:
            logger.debug(f"Reconnecting. Retries left: {retries}")

        if self.on_reconnect:
            self.on_reconnect(self, retries)

    def _on_noreconnect(self):
        """
        This function is called when the WebSocket connection is not re-established after a
        disconnection to stop the reconnection attempts
        """
        if self.debug:
            logger.debug("No more retries left")

        if self.on_noreconnect:
            self.on_noreconnect(self)
