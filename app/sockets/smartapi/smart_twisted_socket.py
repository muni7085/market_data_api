
import json
from kafka import KafkaProducer


import struct
from pathlib import Path
from typing import List, Dict

from app.utils.common.logger import get_logger
from app.utils.connections import SmartApiConnection
from app.utils.smartapi.smart_socket_types import (
    SubscriptionMode,
    ExchangeType,
    SubscriptionAction,
)
import time
import logging
from app.sockets.twisted_socket import MarketDatasetTwistedSocket

logger = get_logger(Path(__file__).name,logging.DEBUG)


class SmartApiTicker(MarketDatasetTwistedSocket):
    WEBSOCKET_URL = "wss://smartapisocket.angelone.in/smart-stream"
    LITTLE_ENDIAN_BYTE_ORDER = "<"
    TOKEN_MAP = {}

    def __init__(
        self,
        auth_token: str,
        api_key: str,
        client_code: str,
        feed_token: str,
        correlation_id: str,
        subscription_mode: SubscriptionMode,
        on_data_save_callback=None,
        debug=False,
    ):
        self.ping_interval = 5
        self.headers = {
            "Authorization": auth_token,
            "x-api-key": api_key,
            "x-client-code": client_code,
            "x-feed-token": feed_token,
        }

        self.sanity_check()
        self.RESUBSCRIBE = False
        self._tokens = []
        self.subscription_mode = subscription_mode
        self.correlation_id = correlation_id
        self.on_data_save_callback = on_data_save_callback
        self.counter = 0

        self.subscribed_tokens = {}
        self.tick_counter={}
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        super().__init__(debug=debug)

    def sanity_check(self):
        for key, value in self.headers.items():
            assert value, f"{key} is empty"

    def set_tokens(self, tokens: List[Dict[str, int | Dict[str, str]]]):
        """
        Set the tokens to subscribe to the WebSocket connection

        Parameters
        ----------
        tokens: ``List[Dict[str, int | Dict[str, str]]]``
            A list of dictionaries containing the exchange type and the tokens to subscribe
            e.g., [{"exchangeType": 1, "tokens": {"token1": "name1", "token2": "name2"}}]
        """
        assert isinstance(tokens, list)

        for token in tokens:
            assert isinstance(token, dict)
            assert "exchangeType" in token
            assert "tokens" in token

            exchange_type = ExchangeType.get_exchange(token["exchangeType"])
            assert isinstance(token["tokens"], dict)
            self._tokens.append(
                {
                    "exchangeType": exchange_type.value,
                    "tokens": list(token["tokens"].keys()),
                }
            )
            self.TOKEN_MAP.update(token["tokens"])


    def subscribe(self, tokens: List[Dict[str, int | Dict[str, str]]]):
        """
        Subscribe to the specified tokens on the WebSocket connection.
        After subscribing, the WebSocket connection will receive data for the specified tokens.
        Based on the subscription mode, the received data will be different.
        Ref: https://smartapi.angelbroking.com/docs/WebSocket2
        
        Parameters
        ----------
        tokens: ``List[Dict[str, int | Dict[str, str]]]``
            A list of dictionaries containing the exchange type and the tokens to subscribe
            e.g., [{"exchangeType": 1, "tokens": {"token1": "name1", "token2": "name2"}}]
        """
        
        if self.debug:
           logger.debug(f"Subscribing to {tokens}") 

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
            for token in tokens[0]["tokens"]:
                self.subscribed_tokens[token] = self.subscription_mode.value
                
            return True
        except Exception as e:
            logger.error(f"Error while sending message: {e}")
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
        if self.RESUBSCRIBE:
            self.subscribe(self.subscribed_tokens.keys())


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
            logger.exception(f"Error in parsing binary data: {e}")

    def _on_message(self, ws, payload, is_binary):
        
        data=self.decode_data(payload)
        data['name']=self.TOKEN_MAP.get(data['token'])
        data['socket_name']="smartapi"
        data['retrived_timestamp']=str(time.time())
        self.producer.send('muni', json.dumps(data).encode('utf-8'))
        self.producer.flush()
        logger.info(self.counter)
        self.counter+=1

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
            cfg.get("correlation_id", None),
            SubscriptionMode.get_subscription_mode(
                cfg.get("subscription_mode", "snap_quote")
            ),
            on_data_save_callback,
            debug=False,
        )
