from logzero import logger
from app.sockets.smartapi.smart_websocket_v2 import SmartWebSocketV2

total_tokens = []
class DataWebSocket(SmartWebSocketV2):
    def __init__(
        self,
        auth_token: str,
        api_key: str,
        client_code: str,
        feed_token: str,
        tokens_list: dict,
        correlation_id: str,
        mode: int,
    ) -> None:
        super().__init__(auth_token, api_key, client_code, feed_token)
        self.correlation_id = correlation_id
        self.mode = mode
        self.tokens_list = tokens_list
        self.counter = 0
        self.max_count = 10
        self.total_tokens = []

    def on_open(self, wsapp):
        logger.info("on websocket open")
        self.subscribe(self.correlation_id, self.mode, self.tokens_list)

    def on_data(self, wsapp, message):
        self.counter += 1
        if self.counter == self.max_count:
            total_tokens.append(self.total_tokens)
            self.total_tokens = []
            self.counter = 0
        
        if isinstance(message,dict):
            format_msg = {
            message["token"]: {
                "ltp": message["last_traded_price"],
                "open": message["open_price_of_the_day"],
                "high": message["high_price_of_the_day"],
                "low": message["low_price_of_the_day"],
                "prev_close": message["closed_price"],
                "last_traded_timestamp":message["last_traded_timestamp"],
            }
        }

            print(format_msg)
            self.total_tokens.append(format_msg)

    def on_error(self, wsapp, error):
        logger.error(error)

    def on_close(self, wsapp):
        for t in total_tokens:
            print("*"*50)
            print(t)
            print(f"total tokens: {len(t)}")
            print("#"*50)


        logger.info("Close")
