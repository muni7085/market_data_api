import sys
import time
import json
import logging
import threading
from pathlib import Path
from datetime import datetime
from autobahn.websocket.protocol import NoneType
from autobahn.websocket.types import ConnectionResponse
from twisted.internet import reactor, ssl
from twisted.python import log as twisted_log
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
    connectWS,
)
from app.utils.common.logger import get_logger
from app.utils.connections import SmartApiConnection
from app.utils.smartapi.smart_socket_types import (
    SubscriptionMode,
    ExchangeType,
    SubscriptionAction,
)

logger = get_logger(Path(__file__).name)
print(logger)


class SmartApiTickerClientProtocol(WebSocketClientProtocol):

    PING_INTERVAL = 2.5
    KEEPALIVE_INTERVAL = 5

    _next_ping = None
    _next_pong_check = None
    _last_pong_time = None
    _last_ping_time = None

    def __init__(self, *args, **kwargs):
        super(SmartApiTickerClientProtocol, self).__init__(*args, **kwargs)

    def onConnect(self, response):

        self.factory.ws = self

        if self.factory.on_connect:
            self.factory.on_connect(self)

        logger.info(f"Connected to {response.peer}")

        self.factory.resetDelay()

    def onOpen(self):
        logger.info("Connection opened")

        self._loop_ping()

        self._loop_pong_check()

        if self.factory.on_open:
            self.factory.on_open(self)

    def onMessage(self, payload, isBinary):
        if self.factory.on_message:
            self.factory.on_message(self, payload, isBinary)

    def onClose(self, was_clean, code, reason):
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

    def onPing(self, payload):
        if self._last_ping_time and self.factory.debug:
            logger.debug(f"Last pong was received at {time.time-self._last_pong_time}")

        self._last_ping_time = time.time()

        if self.factory.debug:
            logger.debug(f"Received ping {payload}")

    def _loop_ping(self):
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


class SmartApiTickerClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    protocol = SmartApiTickerClientProtocol
    maxDelay = 5
    maxRetries = 10

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
        super(SmartApiTickerClientFactory, self).__init__(*args, **kwargs)

    def startedConnecting(self, connector):
        if not self._last_connection_time and self.debug:
            logger.debug("Connection started")
        self._last_connection_time = time.time()

    def clientConnectionFailed(self, connector, reason):
        if self.retries > 0:
            logger.error(f"Connection failed. Reason: {reason}")
            logger.info(
                f"Trying to reconnect in {int(round(self.delay))}. Retries left: {self.retries}"
            )

            if self.on_reconnect:
                self.on_reconnect(self.retries)

        self.retry(connector)
        self.send_noreconnect()

    def clientConnectionLost(self, connector, reason):
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
        if self.maxRetries and (self.retries > self.maxRetries):
            if self.debug:
                logger.debug(
                    f"Max {self.maxRetries} retries reached. Stopping the connection"
                )

                self.stop()
            if self.on_noreconnect:
                self.on_noreconnect()


class SmartApiTicker(object):
    WEBSOCKET_URI = "wss://smartapisocket.angelone.in/smart-stream"
    LITTLE_ENDIAN_BYTE_ORDER = "<"
    _is_first_connect = True

    def __init__(
        self,
        auth_token: str,
        api_key: str,
        client_code: str,
        feed_token: str,
        max_retries: int,
        correlation_id: str,
        subscription_mode: SubscriptionMode,
        on_data_save_callback=None,
        debug=False,
        reconnect=True,
    ):
        self._auth_token = auth_token
        self.__api_key = api_key
        self.__client_code = client_code
        self.__feed_token = feed_token
        self.ping_interval = 5
        self.sanity_check()
        self.__headers = {
            "Authorization": self._auth_token,
            "x-api-key": self.__api_key,
            "x-client-code": self.__client_code,
            "x-feed-token": self.__feed_token,
        }
        self.resubscribe = False
        self.little_endian = "<"
        self.max_retries = max_retries
        self._tokens = []
        self.token_map = {}
        self.subscription_mode = subscription_mode
        self.correlation_id = correlation_id
        self.on_data_save_callback = on_data_save_callback
        self.counter = 0
        self.total_tokens = []
        self.max_count = 10
        self.reconnect_max_tries = 5
        self.reconnect = reconnect
        self.reconnect_max_delay = 5
        self.connection_timeout = 5
        self.debug = debug

        self.ws = None

        self.on_tick = None
        self.on_connect = None
        self.on_open = None
        self.on_message = None
        self.on_error = None
        self.on_close = None
        self.on_reconnect = None
        self.on_noreconnect = None

        self.on_order_update = None

        self.subscribed_tokens = {}

    def sanity_check(self):
        if not self._auth_token:
            raise ValueError("Auth token is required")
        if not self.__api_key:
            raise ValueError("API key is required")
        if not self.__client_code:
            raise ValueError("Client code is required")
        if not self.__feed_token:
            raise ValueError("Feed token is required")

    def set_tokens(self, tokens: list):
        assert isinstance(tokens, list)
        for token in tokens:
            assert isinstance(token, dict)
            assert "exchangeType" in token
            assert "tokens" in token
            exchange = ExchangeType.get_exchange(token["exchangeType"])
            assert isinstance(token["tokens"], dict)
            self._tokens.append(
                {"exchangeType": exchange.value, "tokens": list(token["tokens"].keys())}
            )
            self.token_map.update(token["tokens"])

    def _create_connection(self, url, **kwargs):
        self.factory = SmartApiTickerClientFactory(url, **kwargs)
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
        self._create_connection(self.WEBSOCKET_URI, proxy=proxy, headers=self.__headers)

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
                self.wesocket_thread = threading.Thread(target=reactor.run, kwargs=opts)
                self.websocket_thread.deamon = True
                self.websocket_thread.start()
            else:
                reactor.run(**opts)

    def is_connected(self):
        if self.ws and self.ws.state == self.ws.STATE_OPEN:
            return True
        return False

    def _close(self, code=None, reason=None):
        if self.ws:
            self.ws.sendClose(code, reason)
            self.ws = None

    def close(self, code=None, reason=None):
        self.stop_retry()
        self._close(code, reason)

    def stop(self):
        reactor.stop()

    def stop_retry(self):
        if self.factory:
            self.factory.stopTrying()

    def subscribe(self, tokens=None):
        request_data = {
            "correlationId": self.correlation_id,
            "action": SubscriptionAction.SUBSCRIBE.value,
            "params": {
                "mode": self.subscription_mode.value,
                "exchange": tokens,
            },
        }
        try:
            self.ws.sendMessage(json.dumps(request_data).encode("utf-8"))
            for token in tokens:
                self.subscribed_tokens[token] = self.subscription_mode.value
            return True
        except Exception as e:
            self._close(reason="Error while sending message: {}".format(e))
            raise

    def unsubscribe(self, tokens=None):
        request_data = {
            "correlationId": self.correlation_id,
            "action": SubscriptionAction.UNSUBSCRIBE.value,
            "params": {
                "mode": self.subscription_mode.value,
                "exchange": tokens,
            },
        }
        try:
            self.ws.sendMessage(json.dumps(request_data).encode("utf-8"))
            for token in tokens:
                self.subscribed_tokens.pop(token)
            return True
        except Exception as e:
            self._close(reason="Error while sending message: {}".format(e))
            raise

    def resubscribe(self):
        if self.resubscribe:
            self.subscribe(self.subscribed_tokens.keys())

    def _on_connect(self, ws, response):
        self.ws = ws
        if self.debug:
            logger.debug("Connected")
        if self.on_connect:
            self.on_connect(ws, response)

    def _on_close(self, ws, code, reason):
        if self.debug:
            logger.debug(f"Connection closed. Code: {code}, Reason: {reason}")
        if self.on_close:
            self.on_close(ws, code, reason)

    def _on_error(self, ws, code, reason):
        if self.debug:
            logger.debug(f"Error. Code: {code}, Reason: {reason}")
        if self.on_error:
            self.on_error(ws, code, reason)

    def _on_message(self, ws, payload, is_binary):
        logger.debug(f"Received message: {payload}")
        logger.debug(f"Is binary: {is_binary}")

    def _on_open(self, ws):
        logger.info(f"_on_open called")
        if not self._is_first_connect:
            self.resubscribe()
        else:
            self.subscribe(self._tokens)
            
        self._is_first_connect = False
        if self.on_open:
            self.on_open(self)

    def _on_reconnect(self, retries):
        if self.debug:
            logger.debug(f"Reconnecting. Retries left: {retries}")
        if self.on_reconnect:
            self.on_reconnect(self, retries)

    def _on_noreconnect(self):
        if self.debug:
            logger.debug("No more retries left")
        if self.on_noreconnect:
            self.on_noreconnect(self)

    @staticmethod
    def initialize_socket(cfg, on_data_save_callback=None):
        smartapi_connection = SmartApiConnection.get_connection()
        auth_token = smartapi_connection.get_auth_token()
        feed_token = smartapi_connection.api.getfeedToken()
        api_key = smartapi_connection.credentials.api_key
        client_code = smartapi_connection.credentials.client_id
        return SmartApiTicker(
            auth_token,
            api_key,
            client_code,
            feed_token,
            cfg.get("max_retries", 5),
            cfg.get("correlation_id", None),
            SubscriptionMode.get_subscription_mode(
                cfg.get("subscription_mode", "snap_quote")
            ),
            on_data_save_callback,
            debug=True
        )
