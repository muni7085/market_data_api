from app.sockets.async_market_data_socket import AsyncMarketDataSocket
from app.utils.connections import SmartApiConnection
from app.utils.smartapi.smart_socket_types import (
    SubscriptionMode,
    ExchangeType,
    SubscriptionAction,
)
import websockets
import struct
from app.utils.common.logger import get_logger
import json
from pathlib import Path
import asyncio

logger = get_logger(Path(__file__).name)


class SmartSocket(AsyncMarketDataSocket):
    WEBSOCKET_URI = "wss://smartapisocket.angelone.in/smart-stream"
    LITTLE_ENDIAN_BYTE_ORDER = "<"

    def __init__(
        self,
        auth_token: str,
        api_key: str,
        client_code: str,
        feed_token: str,
        max_retries: int,
        correlation_id: str,
        subscription_mode: SubscriptionMode,
    ):
        self._auth_token = auth_token
        self.__api_key = api_key
        self.__client_code = client_code
        self.__feed_token = feed_token
        self.sanity_check()
        self.__headers = {
            "Authorization": self._auth_token,
            "x-api-key": self.__api_key,
            "x-client-code": self.__client_code,
            "x-feed-token": self.__feed_token,
        }
        self.little_endian = "<"
        self.max_retries = max_retries
        self._tokens = []
        self.subscription_mode = subscription_mode
        self.correlation_id = correlation_id

    def _unpack_data(self, binary_data, start, end, byte_format="I"):
        """
        Unpack Binary Data to the integer according to the specified byte_format.
        This function returns the tuple
        """
        return struct.unpack(
            self.LITTLE_ENDIAN_BYTE_ORDER + byte_format, binary_data[start:end]
        )

    def sanity_check(self):
        if not self._auth_token:
            raise ValueError("Auth token is required")
        if not self.__api_key:
            raise ValueError("API key is required")
        if not self.__client_code:
            raise ValueError("Client code is required")
        if not self.__feed_token:
            raise ValueError("Feed token is required")

    async def decode_data(self, binary_data):
        """
        Parses binary data received from the websocket and returns a dictionary containing the parsed data.

        Parameters:
        -----------
        binary_data: `bytes`
            The binary data received from the websocket.

        Returns:
        -------
        dict:
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
            logger.exception(f"Error in parsing binary data: {e}")

    async def on_data(self, data):
        # TODO: Implement the logic to handle the data
        """
        Callback function that is called when data is received from the websocket connection.

        Parameters:
        -----------
        wsapp: `websocket.WebSocketApp`
            The websocket connection object.
        data: `str`
            The data received from the websocket connection.
        data_type: `int`
            The type of data received from the websocket connection.
        continue_flag: `bool`
            A flag indicating whether the data is complete or partial.
        """

        parsed_data = await self.decode_data(data)
        format_msg = parsed_data
        if isinstance(parsed_data, dict):
            format_msg = {
                parsed_data["token"]: {
                    "ltp": parsed_data["last_traded_price"],
                    "open": parsed_data["open_price_of_the_day"],
                    "high": parsed_data["high_price_of_the_day"],
                    "low": parsed_data["low_price_of_the_day"],
                    "prev_close": parsed_data["closed_price"],
                    "last_traded_timestamp": parsed_data["last_traded_timestamp"],
                }
            }
            
            with open("test.txt", "a+") as f:
                f.write(json.dumps(format_msg))
                
        logger.info(f"Received data: {format_msg}")

    async def subscribe(self, ws):
        try:
            request_data = {
                "correlationID": self.correlation_id,
                "action": SubscriptionAction.SUBSCRIBE.value,
                "params": {
                    "mode": self.subscription_mode.value,
                    "tokenList": self._tokens,
                },
            }
            logger.info(f"Subscribing to websocket with data: {request_data}")
            
            await ws.send(json.dumps(request_data))
            
        except Exception as e:
            logger.exception(f"Error in subscribing to websocket: {e}")

    async def on_open(self, ws):
        logger.info("Websocket connection opened")
        await self.subscribe(ws)

    def set_tokens(self, tokens: list):
        assert isinstance(tokens, list)
        for token in tokens:
            assert isinstance(token, dict)
            assert "exchangeType" in token
            assert "tokens" in token
            exchange = ExchangeType.get_exchange(token["exchangeType"])
            assert isinstance(token["tokens"], list)
            self._tokens.append(
                {"exchangeType": exchange.value, "tokens": token["tokens"]}
            )

    async def connect(self):
        async for websocket in websockets.connect(
            self.WEBSOCKET_URI, extra_headers=self.__headers
        ):
            try:
                await self.on_open(websocket)
                async for message in websocket:
                    await asyncio.sleep(0.1)
                    await self.on_data(websocket, message, 1, False)

            except websockets.exceptions.ConnectionClosed as e:
                logger.error(f"Websocket connection closed: {e}")
            except Exception as e:
                logger.exception(f"Error occurred during websocket connection: {e}")

    @staticmethod
    def initialize_socket(cfg):
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
            cfg.get("max_retries", 5),
            cfg.get("correlation_id", None),
            SubscriptionMode.get_subscription_mode(
                cfg.get("subscription_mode", "snap_quote")
            ),
        )
