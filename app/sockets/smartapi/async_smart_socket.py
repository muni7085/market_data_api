from app.sockets.async_market_data_socket import AsyncMarketDataSocket
from app.utils.connections import SmartApiConnection
from app.utils.smartapi.smart_socket_types import (
    SubscriptionMode,
    ExchangeType,
    SubscriptionAction,
)
import threading
import asyncio
import websockets
import struct
from app.utils.common.logger import get_logger
import json
import time
from app.database.sqlite.async_sqlite_db_connection import get_async_sqlite_session
from pathlib import Path
from app.database.sqlite.models.websocket_models import WebsocketLTPData
import asyncio
import os

logger = get_logger(Path(__file__).name)


class SmartSocket(AsyncMarketDataSocket):
    token_map = None
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
        thread_id: int = 0,
        queue=None
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
        self.counter = 0
        self.total_tokens = []
        self.queue = queue
        self.max_count = 10
        self.data_counter = 0
        self.thread_id = thread_id
        
        # Start the database saving thread
        self.db_thread = threading.Thread(target=self.start_db_saving_loop)
        self.db_thread.start()

    def start_db_saving_loop(self):
        asyncio.run(self.save_to_db())

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
        logger.info(f"Data received {self.thread_id}: {self.data_counter}")
        self.data_counter += 1
        
        try:
            # self.total_tokens.append(data)
            # self.counter += 1
            # if self.counter == self.max_count:
            #     self.queue.put_nowait(self.total_tokens)
            #     self.total_tokens = []
            #     self.counter = 0
            self.queue.put_nowait(data)

        except Exception as e:
            logger.error(f"Error in processing data: {e}")

    async def save_to_db(self, batch_size=100):
        session_maker = get_async_sqlite_session()
        session = await session_maker.__anext__()
        buffer = []
        try:
            while True:
                tokens = self.queue.get()
                buffer.append(tokens)
                if len(buffer) >= batch_size:
                    await self.save_batch_to_db(session, buffer)
                    buffer.clear()
                self.queue.task_done()
        except Exception as e:
            logger.error(f"Error in saving data to database: {e}")
        finally:
            if buffer:
                await self.save_batch_to_db(session, buffer)
            logger.info("Saved data to database...")

    async def save_batch_to_db(self, session, buffer):
        for token_data in buffer:
            parsed_data = await self.decode_data(token_data)
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
            assert isinstance(token["tokens"], dict)
            self._tokens.append(
                {"exchangeType": exchange.value, "tokens": list(token["tokens"].keys())}
            )

    async def connect(self):
       async with websockets.connect(self.WEBSOCKET_URI, extra_headers=self.__headers) as websocket:
            
            logger.info(f"Connected to websocket with {self.thread_id}")
            start = time.time()
            try:
                await self.on_open(websocket)
                async for message in websocket:
                    await self.on_data(message)
                logger.info(f"Time taken: {time.time()-start}")

            # except websockets.exceptions.ConnectionClosed as e:
            #     logger.error(f"Websocket connection closed: {e}")
            except Exception as e:
                logger.exception(f"Error occurred during websocket connection: {e}")

    @staticmethod
    def initialize_socket(cfg,queue):
        smartapi_connection = None
        auth_token = None
        feed_token = None
        api_key = None
        client_code = None

        # Check if credentials are already cached
        if os.path.exists("credentials_cache.json"):
            logger.info("Loading cached credentials")
            with open("credentials_cache.json", "r") as file:
                cached_credentials = json.load(file)
            if (
                cached_credentials.get("auth_token")
                and cached_credentials.get("api_key")
                and cached_credentials.get("client_code")
                and cached_credentials.get("feed_token")
            ):
                auth_token = cached_credentials["auth_token"]
                api_key = cached_credentials["api_key"]
                client_code = cached_credentials["client_code"]
                feed_token = cached_credentials["feed_token"]

        # If credentials are not cached, fetch them and cache them
        if not auth_token or not api_key or not client_code or not feed_token:
            smartapi_connection = SmartApiConnection.get_connection()
            auth_token = smartapi_connection.get_auth_token()
            feed_token = smartapi_connection.api.getfeedToken()
            api_key = smartapi_connection.credentials.api_key
            client_code = smartapi_connection.credentials.client_id

            # Cache the credentials
            credentials = {
                "auth_token": auth_token,
                "api_key": api_key,
                "client_code": client_code,
                "feed_token": feed_token,
            }
            with open("credentials_cache.json", "w") as file:
                json.dump(credentials, file)

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
            cfg.get("thread_id", 0),
            queue=queue
        )
