from app.sockets.market_data_socket import MarketDataSocket
import websocket
from app.utils.connections import SmartApiConnection
from app.utils.smartapi.smart_socket_types import (
    SubscriptionMode,
    ExchangeType,
    SubscriptionAction,
)
import asyncio
from app.database.sqlite.models.websocket_models import WebsocketLTPData
import struct
from app.utils.common.logger import get_logger
from app.database.sqlite.sqlite_db_connection import get_session
from app.database.sqlite.async_sqlite_db_connection import get_async_sqlite_session
import ssl
import time
import json
from pathlib import Path

logger = get_logger(Path(__file__).name)


class SmartSocket(MarketDataSocket):
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
        on_data_save_callback=None,
    ):
        super().__init__(auth_token)
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
        self.queue = asyncio.Queue()
        self.max_count = 10
        
    

    def sanity_check(self):
        if not self.auth_token:
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

    def subscribe(self, wsapp):
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
            logger.info(wsapp)

            wsapp.send(json.dumps(request_data))
            self.resubscribe = True
        except Exception as e:
            logger.exception(f"Error in subscribing to websocket: {e}")

    def on_message(self, wsapp, message):
        pass

    def on_error(self, wsapp, error):
        if self.max_retries > 0:
            print("Attempting to resubscribe/reconnect...")
            self.max_retries -= 1
            try:
                wsapp.close()
                self.connect()
            except Exception as e:
                logger.error("Error occurred during resubscribe/reconnect:", str(e))
        else:
            logger.warning(f"Max retries reached. Closing connection. Error: {error}")
            wsapp.close()

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

    def on_data(self, wsapp, data, data_type, continue_flag):
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
        try:
            self.total_tokens.append(data)
            self.counter += 1
            if self.counter == self.max_count:
                self.queue.put_nowait(self.total_tokens)
                self.total_tokens = []
                self.counter = 0

        except Exception as e:
            logger.error(f"Error in processing data: {e}")

    def on_open(self, wsapp):
        logger.info("Websocket connection opened")
        self.subscribe(wsapp)

    async def save_to_db(self):
        logger.info("Saving data to database...")
        session = await anext(get_async_sqlite_session())
        try:

            while True:
                tokens = await self.queue.get()
                for token_data in tokens:
                    parsed_data = self.decode_data(token_data)
                    if isinstance(parsed_data, dict):
                        format_msg = WebsocketLTPData(
                            timestamp=str(time.time()),
                            symbol=self.token_map[parsed_data["token"]],
                            token=parsed_data["token"],
                            ltp=parsed_data["last_traded_price"],
                            open=parsed_data["open_price_of_the_day"],
                            high=parsed_data["high_price_of_the_day"],
                            low=parsed_data["low_price_of_the_day"],
                            close=parsed_data["closed_price"],
                            last_traded_time=parsed_data["last_traded_timestamp"],
                        )
                    session.add(format_msg)
                await session.commit()
                self.queue.task_done()
        except Exception as e:
            logger.error(f"Error in saving data to database: {e}")

    async def connect(self):
        try:
            self.wsapp = websocket.WebSocketApp(
                self.WEBSOCKET_URI,
                header=self.__headers,
                on_data=self.on_data,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open,
            )

            logger.info("Connecting to websocket...")
            self.wsapp.run_forever(
                sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_interval=self.ping_interval,
            )
        except Exception as e:
            logger.exception(f"Error in connecting to websocket: {e}")

    def on_close(self):
        try:
            self.wsapp.close()
        except Exception as e:
            logger.error(f"Error in closing websocket connection: {e}")

    def on_ping(self, ws, message):
        pass

    def on_pong(self, ws, message):
        pass

    def unsubscribe(self, ws):
        pass

    @staticmethod
    def initialize_socket(cfg, on_data_save_callback=None):
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
            on_data_save_callback,
        )
