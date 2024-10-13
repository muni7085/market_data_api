import json
import struct
import time
from pathlib import Path
from typing import Dict, List, cast

from app.sockets.twisted_socket import MarketDataTwistedSocket
from app.sockets.websocket_client_protocol import MarketDataWebScoketClientProtocol
from app.utils.common.logger import get_logger
from app.utils.smartapi.connection import SmartApiConnection
from app.utils.smartapi.smartsocket_types import (
    ExchangeType,
    SubscriptionAction,
    SubscriptionMode,
)

logger = get_logger(Path(__file__).name, log_level="DEBUG")


class SmartSocket(MarketDataTwistedSocket):
    """
    SmartSocket is a class that connects to the SmartAPI WebSocket server and subscribes
    to the specified tokens. It receives the data for the subscribed tokens and parses
    the data to extract the required information for the subscribed tokens. The parsed
    data is then sent to the callback function for further processing or saving.

    Attributes
    ----------
    WEBSOCKET_URL: ``str``
        The URL of the SmartAPI WebSocket server
    LITTLE_ENDIAN_BYTE_ORDER: ``str``
        The byte order for the binary data received from the WebSocket server
    TOKEN_MAP: ``Dict[str, Tuple[str, ExchangeType]]``
        A dictionary that maps the token to the name and exchange type of the token
    auth_token: ``str``
        The authorization token for the SmartAPI WebSocket server
    api_key: ``str``
        The API key for the SmartAPI WebSocket server connection
    client_code: ``str``
        The client code is the angel broking client id which is used to
        login to the angel broking account
    feed_token: ``str``
        The feed token is used to authenticate the user to the SmartAPI WebSocket server
    correlation_id: ``str``
        The correlation id is used to uniquely identify the WebSocket connection which
        is useful for debugging and logging purposes in multi-connection scenarios
    subscription_mode: ``SubscriptionMode``
        The subscription mode is used to specify the type of data to receive from
        the WebSocket server. The subscription mode can be either "quote", "snap_quote",
        or "full"
    on_data_save_callback: ``Callable[[str], None]``, ( default = None )
        The callback function that is called when the data is received from the
        WebSocket server
    debug: ``bool``, ( default = False )
        A flag to enable or disable the debug mode for the WebSocket connection.
        Enable this flag in development mode to get detailed logs for debugging
        purposes
    """

    WEBSOCKET_URL = "wss://smartapisocket.angelone.in/smart-stream"
    LITTLE_ENDIAN_BYTE_ORDER = "<"
    TOKEN_MAP: dict[str, tuple[str, ExchangeType]] = {}

    def __init__(
        self,
        auth_token: str,
        api_key: str,
        client_code: str,
        feed_token: str,
        correlation_id: str,
        subscription_mode: SubscriptionMode,
        on_data_save_callback,
        debug,
    ):
        self.ping_interval = 5
        self.headers = {
            "Authorization": auth_token,
            "x-api-key": api_key,
            "x-client-code": client_code,
            "x-feed-token": feed_token,
        }

        self.sanity_check()
        self.subscription_mode = subscription_mode
        self.correlation_id = correlation_id
        self.on_data_save_callback = on_data_save_callback
        self.counter = 0

        self.subscribed_tokens: dict[str, int] = {}
        super().__init__(debug=debug)

    def sanity_check(self):
        """
        Check if the headers are set correctly and raise an exception if
        any of the headers are empty
        """
        for key, value in self.headers.items():
            assert value, f"{key} is empty"

    def set_tokens(
        self,
        tokens_with_exchanges: (
            dict[str, int | dict[str, str]] | list[dict[str, int | dict[str, str]]]
        ),
    ):
        """
        Set the tokens to subscribe to the WebSocket connection

        Parameters
        ----------
        tokens: ``Dict[str, int | Dict[str, str]] | List[Dict[str, int | Dict[str, str]]]``
            A list of dictionaries containing the exchange type and the tokens to subscribe
            e.g., [{"exchangeType": 1, "tokens": {"token1": "name1", "token2": "name2"}}]
                or {"exchangeType": 1, "tokens": ["token1", "token2"]}
        """
        if isinstance(tokens_with_exchanges, dict):
            tokens_with_exchanges = [tokens_with_exchanges]

        for token_exchange_info in tokens_with_exchanges:
            if (
                "exchangeType" not in token_exchange_info
                or "tokens" not in token_exchange_info
                or not token_exchange_info["tokens"]
                or not token_exchange_info["exchangeType"]
            ):
                logger.error(
                    "Invalid token format %s, skipping token", token_exchange_info
                )
                continue

            exchange_type = ExchangeType.get_exchange(
                cast(int, token_exchange_info["exchangeType"])
            )

            self._tokens.append(
                {
                    "exchangeType": exchange_type.value,
                    "tokens": list(cast(dict, token_exchange_info["tokens"]).keys()),
                }
            )
            self.TOKEN_MAP.update(
                {
                    k: (v, exchange_type)
                    for k, v in cast(dict, token_exchange_info["tokens"]).items()
                }
            )

    def subscribe(self, tokens: List[Dict[str, int | List[str]]]):
        """
        Subscribe to the specified tokens on the WebSocket connection.
        After subscribing, the WebSocket connection will receive data
        for the specified tokens. Based on the subscription mode, the
        received data will be different.
        Ref: https://smartapi.angelbroking.com/docs/WebSocket2

        Parameters
        ----------
        tokens: ``[Dict[str, int | List[str]]]``
            A list of dictionaries containing the exchange type and the tokens to subscribe
            e.g., [{"exchangeType": 1, "tokens": ["token1", "token2"]}]
        """

        if self.debug:
            logger.debug("Subscribing to tokens: %s", tokens)

        if not tokens:
            logger.error("No tokens to subscribe")
            return False

        request_data = {
            "correlationID": self.correlation_id,
            "action": SubscriptionAction.SUBSCRIBE.value,
            "params": {
                "mode": self.subscription_mode.value,
                "tokenList": tokens,
            },
        }
        try:
            self.ws.sendMessage(json.dumps(request_data).encode("utf-8"))

            for token_info in tokens:
                for t in cast(list, token_info["tokens"]):
                    self.subscribed_tokens[t] = cast(int, token_info["exchangeType"])

            return True
        except Exception as e:
            logger.error("Error while sending message: %s", e)
            self._close(reason=f"Error while sending message: {e}")
            raise e

    def unsubscribe(self, tokens=None):
        """
        Unsubscribe from the specified tokens on the WebSocket connection.
        After unsubscribing, the WebSocket connection will no longer receive
        data for the specified tokens.

        Parameters
        ----------
        tokens: ``List[str]``
            A list of tokens to unsubscribe from the WebSocket connection
        """

        if not tokens:
            logger.error("No tokens to unsubscribe")
            return False

        subscribed_tokens = []
        token_exchange_map = {}
        tokens_not_subscribed = []

        for token in tokens:
            if token in self.subscribed_tokens:
                subscribed_tokens.append(token)
                if self.subscribed_tokens[token] not in token_exchange_map:
                    token_exchange_map[self.subscribed_tokens[token]] = []

                token_exchange_map[self.subscribed_tokens[token]].append(token)

            else:
                tokens_not_subscribed.append(token)

        if tokens_not_subscribed:
            logger.error("Tokens not subscribed: %s", tokens_not_subscribed)

        tokens_to_unsubscribe = [
            {"exchangeType": exchange, "tokens": token_list}
            for exchange, token_list in token_exchange_map.items()
        ]

        request_data = {
            "correlationId": self.correlation_id,
            "action": SubscriptionAction.UNSUBSCRIBE.value,
            "params": {
                "mode": self.subscription_mode.value,
                "exchange": tokens_to_unsubscribe,
            },
        }

        try:
            if self.debug:
                logger.debug("Unsubscribing from tokens: %s", tokens_to_unsubscribe)

            self.ws.sendMessage(json.dumps(request_data).encode("utf-8"))

            for token in subscribed_tokens:
                self.subscribed_tokens.pop(token)

            return True
        except Exception as e:
            logger.error("Error while sending message to unsubscribe tokens: %s", e)
            self._close(reason="Error while sending message: {}".format(e))
            raise

    def resubscribe(self):
        """
        Resubscribe to previously subscribed tokens on the WebSocket connection.

        Resubscribes to all previously subscribed tokens. It groups tokens by their
        exchange type and then  calls the subscribe method with the grouped tokens
        """
        tokens_with_exchange = {}

        for token, exchange_type in self.subscribed_tokens.items():
            tokens_with_exchange.setdefault(exchange_type, []).append(token)

        tokens_list = [
            {"exchangeType": exchange_type, "tokens": tokens}
            for exchange_type, tokens in tokens_with_exchange.items()
        ]

        if self.debug:
            logger.debug("Resubscribing to tokens: %s", tokens_list)

        return self.subscribe(tokens_list)

    def _unpack_data(self, binary_data, start, end, byte_format="I"):
        """
        Unpack Binary Data to the integer according to the specified byte_format.
        This function returns the tuple
        """
        return struct.unpack(
            self.LITTLE_ENDIAN_BYTE_ORDER + byte_format, binary_data[start:end]
        )

    def decode_data(self, binary_data):
        """
        Parses binary data received from the websocket and returns a dictionary
        containing the parsed data.

        Parameters
        -----------
        binary_data: ``bytes``
            The binary data received from the websocket.

        Returns:
        -------
        parsed_data: ``Dict[str, Any]``
            A dictionary containing the parsed data.
        """

        parsed_data = {
            "subscription_mode": self._unpack_data(binary_data, 0, 1, byte_format="B")[
                0
            ],
            "exchange_type": self._unpack_data(binary_data, 1, 2, byte_format="B")[0],
            # "token": SmartWebSocketV2._parse_token_value(binary_data[2:27]),
            "token": binary_data[2:27].decode("utf-8").replace("\x00", ""),
            "sequence_number": self._unpack_data(binary_data, 27, 35, byte_format="q")[
                0
            ],
            "exchange_timestamp": self._unpack_data(
                binary_data, 35, 43, byte_format="q"
            )[0],
            "last_traded_price": self._unpack_data(
                binary_data, 43, 51, byte_format="q"
            )[0],
        }
        try:
            parsed_data["subscription_mode_val"] = (
                SubscriptionMode.get_subscription_mode(
                    parsed_data["subscription_mode"]
                ).name
            )

            if parsed_data["subscription_mode"] in [
                SubscriptionMode.QUOTE.value,
                SubscriptionMode.SNAP_QUOTE.value,
            ]:
                parsed_data["last_traded_quantity"] = self._unpack_data(
                    binary_data, 51, 59, byte_format="q"
                )[0]
                parsed_data["average_traded_price"] = self._unpack_data(
                    binary_data, 59, 67, byte_format="q"
                )[0]
                parsed_data["volume_trade_for_the_day"] = self._unpack_data(
                    binary_data, 67, 75, byte_format="q"
                )[0]
                parsed_data["total_buy_quantity"] = self._unpack_data(
                    binary_data, 75, 83, byte_format="d"
                )[0]
                parsed_data["total_sell_quantity"] = self._unpack_data(
                    binary_data, 83, 91, byte_format="d"
                )[0]
                parsed_data["open_price_of_the_day"] = self._unpack_data(
                    binary_data, 91, 99, byte_format="q"
                )[0]
                parsed_data["high_price_of_the_day"] = self._unpack_data(
                    binary_data, 99, 107, byte_format="q"
                )[0]
                parsed_data["low_price_of_the_day"] = self._unpack_data(
                    binary_data, 107, 115, byte_format="q"
                )[0]
                parsed_data["closed_price"] = self._unpack_data(
                    binary_data, 115, 123, byte_format="q"
                )[0]

            if parsed_data["subscription_mode"] == SubscriptionMode.SNAP_QUOTE.value:
                parsed_data["last_traded_timestamp"] = self._unpack_data(
                    binary_data, 123, 131, byte_format="q"
                )[0]
                parsed_data["open_interest"] = self._unpack_data(
                    binary_data, 131, 139, byte_format="q"
                )[0]
                parsed_data["open_interest_change_percentage"] = self._unpack_data(
                    binary_data, 139, 147, byte_format="q"
                )[0]
            return parsed_data
        except Exception as e:
            logger.exception("Error in parsing binary data: %s", e)

    def _on_message(
        self,
        ws: MarketDataWebScoketClientProtocol,
        payload: bytes | str,
        is_binary: bool,
    ):
        """
        Process incoming WebSocket messages and prepare data for callback.

        This method is called whenever a message is received on the WebSocket
        connection. It decodes the payload, enriches the data with additional
        information, and triggers the data save callback if one is set

        Parameters
        ----------
        ws: ``MarketDataWebScoketClientProtocol``
           The websocket client protocol instance
        payload: ``bytes | str``
            The raw message payload received from the WebSocket
        is_binary: ``bool``
            Flag indicating whether the payload is binary data
        """
        if is_binary:
            data = self.decode_data(payload)
        else:
            data = json.loads(payload)

        data["name"] = self.TOKEN_MAP[data["token"]][0]
        data["socket_name"] = "smartapi"
        data["retrieval_timestamp"] = str(time.time())
        data["exchange"] = self.TOKEN_MAP[data["token"]][1].name

        if self.debug:
            logger.debug("Received data: %s", data)

        if self.on_data_save_callback:
            self.on_data_save_callback(json.dumps(data))

    @staticmethod
    def initialize_socket(cfg, on_save_data_callback=None):
        smartapi_connection = SmartApiConnection.get_connection()
        auth_token = smartapi_connection.get_auth_token()
        feed_token = smartapi_connection.api.getfeedToken()
        api_key = smartapi_connection.credentials.api_key
        client_code = smartapi_connection.credentials.client_id

        return SmartSocket(
            auth_token,
            api_key,
            client_code,
            feed_token,
            cfg.get("correlation_id", None),
            SubscriptionMode.get_subscription_mode(
                cfg.get("subscription_mode", "snap_quote")
            ),
            on_save_data_callback,
            debug=cfg.get("debug", False),
        )
