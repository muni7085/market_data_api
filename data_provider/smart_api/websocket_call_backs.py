from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger
from time import perf_counter

class DataWebSocket(SmartWebSocketV2):
    def __init__(
        self,
        auth_token:str,
        api_key:str,
        client_code:str,
        feed_token:str,
        tokens_list:dict,
        correlation_id:str,
        mode:int,
    ) -> None:
        super().__init__(auth_token, api_key, client_code, feed_token)
        self.correlation_id = correlation_id
        self.mode = mode
        self.tokens_list = tokens_list
        self.counter = 0
        self.max_count = 10
        
    def on_open(self, wsapp):
        logger.info("on websocket open")
        self.subscribe(self.correlation_id, self.mode, self.tokens_list)
        # sws.unsubscribe(correlation_id, mode, token_list1)



    def on_data(self, wsapp, message):
        file_mode = "a+"
        # self.counter += 1
        if self.counter <= self.max_count:
            format_msg = {
                message["token"]: {
                    "ltp": message["last_traded_price"],
                    "open": message["open_price_of_the_day"],
                    "high": message["high_price_of_the_day"],
                    "low": message["low_price_of_the_day"],
                    "prev_close": message["closed_price"],
                }
            }

            with open(
                "/home/munikumar/Desktop/python_project/option_chain_api/test.json",
                file_mode,
            ) as fp:
                fp.write(str(format_msg))



    def on_error(self, wsapp, error):
        logger.error(error)

    def on_close(self,wsapp):
        logger.info("Close")
