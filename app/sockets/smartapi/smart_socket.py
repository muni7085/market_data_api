from app.sockets.market_data_socket import MarketDataSocket
import websocket
from app.utils.credentials.credential_manager import get_credentials
from app.utils.connections import SmartApiConnection
from app.utils.smartapi.smart_socket_types import SubscriptionMode, ExchangeType
from app.utils.common.logger import get_logger
import ssl
from pathlib import Path

logger = get_logger(Path(__file__).name)


class SmartSocket(MarketDataSocket):
    WEBSOCKET_URI = "wss://smartapisocket.angelone.in/smart-stream"

    def __init__(
        self,
        auth_token: str,
        api_key: str,
        client_code: str,
        feed_token: str,
        max_retries: int = 5,
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
        self.tokens = []
        self.mode: SubscriptionMode = None

    def sanity_check(self):
        if not self._auth_token:
            raise ValueError("Auth token is required")
        if not self.__api_key:
            raise ValueError("API key is required")
        if not self.__client_code:
            raise ValueError("Client code is required")
        if not self.__feed_token:
            raise ValueError("Feed token is required")

    def on_message(self, ws, message):
        pass

    def on_data(self, ws, message):
        # TODO: Implement the logic to handle the data
        ...

    def on_open(self, ws): ...
    def connect(self, smar):
        try:
            self.wsapp = websocket.WebSocketApp(
                self.WEBSOCKET_URI,
                header=self.__headers,
                on_data=self.on_data,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open,
                on_ping=self.on_ping,
                on_pong=self.on_pong,
            )

            self.wsapp.run_forever(
                sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_interval=self.ping_interval,
            )
        except Exception as e:
            logger.exception(f"Error in connecting to websocket: {e}")

    @staticmethod
    def initialize_socket(self):
        smartapi_connection = SmartApiConnection.get_connection()
        auth_token = smartapi_connection.get_auth_token()
        feed_token = smartapi_connection.api.getfeedToken()
        api_key = smartapi_connection.credentials.api_key
        client_code = smartapi_connection.credentials.client_id
        return SmartSocket(auth_token, api_key, client_code, feed_token)
