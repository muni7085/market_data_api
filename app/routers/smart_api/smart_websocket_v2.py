import struct
import threading
import time
import ssl
import json
import websocket
from datetime import datetime, timedelta
from threading import Timer


class SmartWebSocketV2(object):
    """

    A class representing a WebSocket connection to the Smart API.

    Attributes:
    -----------
    - ROOT_URI (str): The root URI of the Smart API WebSocket.
    - auth_token (str): The authorization token for the WebSocket connection.
    - api_key (str): The API key for the WebSocket connection.
    - client_code (str): The client code for the WebSocket connection.
    - feed_token (str): The feed token for the WebSocket connection.
    - HEART_BEAT_INTERVAL (int): The interval at which to send heartbeats to the WebSocket server.
    - HEART_BEAT_MESSAGE (str): The message to send as a heartbeat to the WebSocket server.
    - wsapp (WebSocketApp): The WebSocketApp instance for the WebSocket connection.

    Methods:
    --------
    - connect(): Connects to the Smart API WebSocket using the provided credentials.
    - _on_open(ws): Callback function for when the WebSocket connection is opened.
    - _on_error(ws, error): Callback function for when an error occurs in the WebSocket connection.
    - _on_close(ws): Callback function for when the WebSocket connection is closed.
    - _on_data(ws, message): Callback function for when a message is received from the WebSocket server.
    - _on_ping(ws, message): Callback function for when a ping message is received from the WebSocket server.
    - _on_pong(ws, message): Callback function for when a pong message is received from the WebSocket server.

    """

    ROOT_URI = "wss://smartapisocket.angelone.in/smart-stream"
    HEART_BEAT_MESSAGE = "ping"
    HEART_BEAT_INTERVAL = 5  # Adjusted to 10s
    LITTLE_ENDIAN_BYTE_ORDER = "<"
    RESUBSCRIBE_FLAG = False
    # HB_THREAD_FLAG = True

    # Available Actions
    SUBSCRIBE_ACTION = 1
    UNSUBSCRIBE_ACTION = 0

    # Possible Subscription Mode
    LTP_MODE = 1
    QUOTE = 2
    SNAP_QUOTE = 3
    DEPTH = 4

    # Exchange Type
    NSE_CM = 1
    NSE_FO = 2
    BSE_CM = 3
    BSE_FO = 4
    MCX_FO = 5
    NCX_FO = 7
    CDE_FO = 13

    # Subscription Mode Map
    SUBSCRIPTION_MODE_MAP = {1: "LTP", 2: "QUOTE", 3: "SNAP_QUOTE", 4: "DEPTH"}

    wsapp = None
    input_request_dict = {}
    current_retry_attempt = 0

    def __init__(
        self, auth_token, api_key, client_code, feed_token, max_retry_attempt=1
    ):
        """
        Initialise the SmartWebSocketV2 instance
        Parameters
        ------
        auth_token: string
            jwt auth token received from Login API
        api_key: string
            api key from Smart API account
        client_code: string
            angel one account id
        feed_token: string
            feed token received from Login API
        """
        self.auth_token = auth_token
        self.api_key = api_key
        self.client_code = client_code
        self.feed_token = feed_token
        self.DISCONNECT_FLAG = True
        self.last_pong_timestamp = None
        self.MAX_RETRY_ATTEMPT = max_retry_attempt

        if not self._sanity_check():
            raise Exception("Provide valid value for all the tokens")

    def _sanity_check(self):
        return True
        # if self.auth_token is None or self.api_key is None or self.client_code is None or self.feed_token is None:
        #     return False
        # return True

    def _on_message(self, wsapp, message):
        """
        Callback function that is called when a message is received from the websocket connection.

        Parameters:
        -----------
        wsapp: `websocket.WebSocketApp`
            The websocket connection object.
        message: `str`
            The message received from the websocket connection.
        """
        if message != "pong":
            parsed_message = self._parse_binary_data(message)
            self.on_message(wsapp, parsed_message)
        else:
            self.on_message(wsapp, message)

    def _on_data(self, wsapp, data, data_type, continue_flag):
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
        if data_type == 2:
            parsed_message = self._parse_binary_data(data)
            self.on_data(wsapp, parsed_message)
        else:
            self.on_data(wsapp, data)

    def _on_open(self, wsapp):
        """
        Callback function that is called when the websocket connection is opened.
        If the RESUBSCRIBE_FLAG is set to True, it will resubscribe to the websocket.
        If the RESUBSCRIBE_FLAG is set to False, it will call the on_open function.
        """
        if self.RESUBSCRIBE_FLAG:
            self.resubscribe()
            self.RESUBSCRIBE_FLAG = False  # Add this line to prevent resubscription on subsequent reconnects
        else:
            self.on_open(wsapp)

    def _on_pong(self, wsapp, data):
        """
        Callback function for handling pong messages received from the server.

        Parameters:
        -----------
        wsapp: `websocket.WebSocketApp`
            The WebSocketApp instance.
        data: `str`
            The message received from the server.
        """

        if data == self.HEART_BEAT_MESSAGE:
            timestamp = time.time()
            formatted_timestamp = time.strftime(
                "%d-%m-%y %H:%M:%S", time.localtime(timestamp)
            )
            print(f"In on pong function ==> {data}, Timestamp: {formatted_timestamp}")
            self.last_pong_timestamp = timestamp
        else:
            # Handle the received feed data here
            self.on_data(wsapp, data)

    def _on_ping(self, wsapp, data):
        """
        Callback function for handling ping messages from the server.

        Parameters:
        -----------
        wsapp: `websocket.WebSocketApp`
            The WebSocketApp instance.
        data: `str`
            The message received from the server.
        """
        timestamp = time.time()
        formatted_timestamp = time.strftime(
            "%d-%m-%y %H:%M:%S", time.localtime(timestamp)
        )
        print(f"In on ping function ==> {data}, Timestamp: {formatted_timestamp}")
        self.last_ping_timestamp = timestamp

    def check_connection_status(self):
        """
        Check the connection status and take appropriate action if a stale connection is detected.
        """
        current_time = time.time()
        if (
            self.last_pong_timestamp is not None
            and current_time - self.last_pong_timestamp > 2 * self.HEART_BEAT_MESSAGE
        ):
            # Stale connection detected, take appropriate action
            self.close_connection()
            self.connect()

    def start_ping_timer(self):
        """
        Starts a timer to send ping messages to the server at regular intervals.
        If a pong message is not received within a certain time frame, the connection is considered stale and reconnected.
        """

        def send_ping():
            """
            Sends a ping message to the server to check if the connection is still active.
            If the connection is stale, it reconnects to the server.
            """
            try:
                current_time = datetime.now()
                if (
                    self.last_pong_timestamp is None
                    or self.last_pong_timestamp
                    < current_time - timedelta(self.HEART_BEAT_MESSAGE)
                ):
                    # print("stale connection detected")
                    # self.wsapp.close()
                    self.connect()
                else:
                    self.last_ping_timestamp = time.time()
            except Exception as e:
                print(f"error: {e}")
                self.wsapp.close()
                self.resubscribe()

        ping_timer = Timer(5, send_ping)
        ping_timer.start()

    def subscribe(self, correlation_id, mode, token_list):
        """
        This Function subscribe the price data for the given token
        Parameters
        ------
        correlation_id: string
            A 10 character alphanumeric ID client may provide which will be returned by the server in error response
            to indicate which request generated error response.
            Clients can use this optional ID for tracking purposes between request and corresponding error response.
        mode: integer
            It denotes the subscription type
            possible values -> 1, 2 and 3
            1 -> LTP
            2 -> Quote
            3 -> Snap Quote
        token_list: list of dict
            Sample Value ->
                [
                    { "exchangeType": 1, "tokens": ["10626", "5290"]},
                    {"exchangeType": 5, "tokens": [ "234230", "234235", "234219"]}
                ]
                exchangeType: integer
                possible values ->
                    1 -> nse_cm
                    2 -> nse_fo
                    3 -> bse_cm
                    4 -> bse_fo
                    5 -> mcx_fo
                    7 -> ncx_fo
                    13 -> cde_fo
                tokens: list of string
        """
        try:
            request_data = {
                "correlationID": correlation_id,
                "action": self.SUBSCRIBE_ACTION,
                "params": {"mode": mode, "tokenList": token_list},
            }

            if self.input_request_dict.get(mode) is None:
                self.input_request_dict[mode] = {}

            for token in token_list:
                if token["exchangeType"] in self.input_request_dict[mode]:
                    self.input_request_dict[mode][token["exchangeType"]].extend(
                        token["tokens"]
                    )
                else:
                    self.input_request_dict[mode][token["exchangeType"]] = token[
                        "tokens"
                    ]

            self.wsapp.send(json.dumps(request_data))
            self.RESUBSCRIBE_FLAG = True

        except Exception as e:
            print(f"subscription error: {e}")

            raise e

    def unsubscribe(self, correlation_id, mode, token_list):
        """
        This function unsubscribe the data for given token
        Parameters
        ------
        correlation_id: string
            A 10 character alphanumeric ID client may provide which will be returned by the server in error response
            to indicate which request generated error response.
            Clients can use this optional ID for tracking purposes between request and corresponding error response.
        mode: integer
            It denotes the subscription type
            possible values -> 1, 2 and 3
            1 -> LTP
            2 -> Quote
            3 -> Snap Quote
        token_list: list of dict
            Sample Value ->
                [
                    { "exchangeType": 1, "tokens": ["10626", "5290"]},
                    {"exchangeType": 5, "tokens": [ "234230", "234235", "234219"]}
                ]
                exchangeType: integer
                possible values ->
                    1 -> nse_cm
                    2 -> nse_fo
                    3 -> bse_cm
                    4 -> bse_fo
                    5 -> mcx_fo
                    7 -> ncx_fo
                    13 -> cde_fo
                tokens: list of string
        """
        try:
            total_tokens = sum(len(token["tokens"]) for token in token_list)
            quota_limit = 1000
            if total_tokens > quota_limit:
                raise Exception(
                    "Quota exceeded: You can subscribe to a maximum of {} tokens.".format(
                        quota_limit
                    )
                )
            else:
                request_data = {
                    "correlationID": correlation_id,
                    "action": self.SUBSCRIBE_ACTION,
                    "params": {"mode": mode, "tokenList": token_list},
                }

                if self.input_request_dict.get(mode, None) is None:
                    self.input_request_dict[mode] = {}

                for token in token_list:
                    if token["exchangeType"] in self.input_request_dict[mode]:
                        self.input_request_dict[mode][token["exchangeType"]].extend(
                            token["tokens"]
                        )
                    else:
                        self.input_request_dict[mode][token["exchangeType"]] = token[
                            "tokens"
                        ]
                self.wsapp.send(json.dumps(request_data))
                self.RESUBSCRIBE_FLAG = True

        except Exception as e:
            print(f"error: {e}")
            raise e

    def resubscribe(self):
        """
        Resubscribes to the market data API with the input request dictionary.
        The input request dictionary contains exchange types and their corresponding tokens.
        """
    
        try:
            for key, val in self.input_request_dict.items():
                token_list = []
                for key1, val1 in val.items():
                    temp_data = {"exchangeType": key1, "tokens": val1}
                    token_list.append(temp_data)
                request_data = {
                    "action": self.SUBSCRIBE_ACTION,
                    "params": {"mode": key, "tokenList": token_list},
                }
                self.wsapp.send(json.dumps(request_data))
        except Exception as e:
            print(f"error: {e}")
            raise e

    def connect(self):
        """
        Connects to the WebSocket server using the provided authentication token, API key, client code, and feed token.
        If the connection is successful, the WebSocketApp instance is stored in self.wsapp and run_forever is called with
        the appropriate arguments. If an exception occurs during the connection process, it is raised.
        """
        headers = {
            "Authorization": self.auth_token,
            "x-api-key": self.api_key,
            "x-client-code": self.client_code,
            "x-feed-token": self.feed_token,
        }

        try:
            self.wsapp = websocket.WebSocketApp(
                self.ROOT_URI,
                header=headers,
                on_open=self._on_open,
                on_error=self._on_error,
                on_close=self._on_close,
                on_data=self._on_data,
                on_ping=self._on_ping,
                on_pong=self._on_pong,
            )
            self.wsapp.run_forever(
                sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_interval=self.HEART_BEAT_INTERVAL,
                ping_payload=self.HEART_BEAT_MESSAGE,
            )
            # self.start_ping_timer()
        except Exception as e:
            print(f"error from connect: {e}")
            raise e

    def close_connection(self):
        """
        Closes the connection.

        Sets RESUBSCRIBE_FLAG to False, DISCONNECT_FLAG to True, and closes the websocket connection if it exists.
        """
        self.RESUBSCRIBE_FLAG = False
        self.DISCONNECT_FLAG = True
        # self.HB_THREAD_FLAG = False
        if self.wsapp:
            self.wsapp.close()

    # def run(self):
    #     while True:
    #         if not self.HB_THREAD_FLAG:
    #             break
    #         self.send_heart_beat()
    #         time.sleep(self.HEAR_BEAT_INTERVAL)

    def send_heart_beat(self):
        """
        Sends a heart beat message to the websocket server.
        """
        try:
            self.wsapp.send(self.HEART_BEAT_MESSAGE)
        except Exception as e:
            print(f"error: {e}")
            raise e

    def _on_error(self, wsapp, error):
        """
        Callback function that is called when an error occurs in the WebSocket connection.

        Parameters:
        -----------
        wsapp: `websocket.WebSocketApp`
            The WebSocketApp instance that encountered the error.
        error: `Exception`
            The error that occurred.

        """
        # self.HB_THREAD_FLAG = False
    
        self.RESUBSCRIBE_FLAG = True
        if self.current_retry_attempt < self.MAX_RETRY_ATTEMPT:
            print("Attempting to resubscribe/reconnect...")
            self.current_retry_attempt += 1
            try:
                self.close_connection()
                self.connect()
            except Exception as e:
                print("Error occurred during resubscribe/reconnect:", str(e))
        else:
            self.close_connection()

    def _on_close(self, wsapp, close_status, close_message):
        # self.HB_THREAD_FLAG = False
        # print(self.wsapp.close_frame)
        self.on_close(wsapp)

    def _parse_binary_data(self, binary_data):
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
            parsed_data["subscription_mode_val"] = self.SUBSCRIPTION_MODE_MAP.get(
                parsed_data["subscription_mode"]
            )

            if parsed_data["subscription_mode"] in [self.QUOTE, self.SNAP_QUOTE]:
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

            if parsed_data["subscription_mode"] == self.SNAP_QUOTE:
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
            print(f"error: {e}")
            raise e

    def _unpack_data(self, binary_data, start, end, byte_format="I"):
        """
        Unpack Binary Data to the integer according to the specified byte_format.
        This function returns the tuple
        """
        return struct.unpack(
            self.LITTLE_ENDIAN_BYTE_ORDER + byte_format, binary_data[start:end]
        )

    @staticmethod
    def _parse_token_value(binary_packet):
        """
        Parses a binary packet to extract a token value.

        Parameters:
        -----------
        binary_packet: `bytes`
            The binary packet to parse.

        Returns:
        -------
        str:
            The extracted token value.
        """
        try:
            token = ""
            for i in range(len(binary_packet)):
                if chr(binary_packet[i]) == "\x00":
                    return token
                token += chr(binary_packet[i])
            return token
        except Exception as e:
            print(f"_parse_token_value error: {e}")

    # def _parse_best_5_buy_and_sell_data(self, binary_data):
    #     def split_packets(binary_packets):
    #         packets = []

    #         i = 0
    #         while i < len(binary_packets):
    #             packets.append(binary_packets[i : i + 20])
    #             i += 20
    #         return packets

    #     best_5_buy_sell_packets = split_packets(binary_data)

    #     best_5_buy_data = []
    #     best_5_sell_data = []

    #     for packet in best_5_buy_sell_packets:
    #         each_data = {
    #             "flag": self._unpack_data(packet, 0, 2, byte_format="H")[0],
    #             "quantity": self._unpack_data(packet, 2, 10, byte_format="q")[0],
    #             "price": self._unpack_data(packet, 10, 18, byte_format="q")[0],
    #             "no of orders": self._unpack_data(packet, 18, 20, byte_format="H")[0],
    #         }

    #         if each_data["flag"] == 0:
    #             best_5_buy_data.append(each_data)
    #         else:
    #             best_5_sell_data.append(each_data)

    #     return {
    #         "best_5_buy_data": best_5_buy_data,
    #         "best_5_sell_data": best_5_sell_data,
    #     }

    # def _parse_depth_20_buy_and_sell_data(self, binary_data):
    #     depth_20_buy_data = []
    #     depth_20_sell_data = []

    #     for i in range(20):
    #         buy_start_idx = i * 10
    #         sell_start_idx = 200 + i * 10

    #         # Parse buy data
    #         buy_packet_data = {
    #             "quantity": self._unpack_data(
    #                 binary_data, buy_start_idx, buy_start_idx + 4, byte_format="i"
    #             )[0],
    #             "price": self._unpack_data(
    #                 binary_data, buy_start_idx + 4, buy_start_idx + 8, byte_format="i"
    #             )[0],
    #             "num_of_orders": self._unpack_data(
    #                 binary_data, buy_start_idx + 8, buy_start_idx + 10, byte_format="h"
    #             )[0],
    #         }

    #         # Parse sell data
    #         sell_packet_data = {
    #             "quantity": self._unpack_data(
    #                 binary_data, sell_start_idx, sell_start_idx + 4, byte_format="i"
    #             )[0],
    #             "price": self._unpack_data(
    #                 binary_data, sell_start_idx + 4, sell_start_idx + 8, byte_format="i"
    #             )[0],
    #             "num_of_orders": self._unpack_data(
    #                 binary_data,
    #                 sell_start_idx + 8,
    #                 sell_start_idx + 10,
    #                 byte_format="h",
    #             )[0],
    #         }

    #         depth_20_buy_data.append(buy_packet_data)
    #         depth_20_sell_data.append(sell_packet_data)

    #     return {
    #         "depth_20_buy_data": depth_20_buy_data,
    #         "depth_20_sell_data": depth_20_sell_data,
    #     }

    # def on_message(self, wsapp, message):
    #     print(message)

    def on_data(self, wsapp, data):
        pass

    def on_close(self, wsapp):
        pass

    def on_open(self, wsapp):
        pass

    def on_error(self):
        pass
