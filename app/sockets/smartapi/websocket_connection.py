from app.utils.smartapi.connection import SmartApiConnection
from app.sockets.smartapi.smart_websocket import DataWebSocket
import json

action = 0
mode = 3
correlation_id = "abcde12345"


def get_tokens(num):
    with open(
        "/home/munikumar/Desktop/python_project/market_data_api/app/data/smart_api/nse_symbols.json",
        "r",
    ) as fp:
        data = json.load(fp)
        tokens = [val for key, val in data.items()]
    return tokens[:num]


tokens = [
    {
        "exchangeType": 1,
        "tokens": ["11536"],
    }
]
smart_api_connection = SmartApiConnection.get_connection()
auth_token = smart_api_connection.get_auth_token()
feed_token = smart_api_connection.api.getfeedToken()
data_websocket = DataWebSocket(
    auth_token,
    smart_api_connection.credentials.api_key,
    smart_api_connection.credentials.client_id,
    feed_token,
    tokens,
    correlation_id,
    mode,
)
data_websocket.connect()
data_websocket.send_heart_beat()
