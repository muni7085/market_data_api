from app.utils.smartapi.connection import SmartApiConnection
from app.utils.smartapi.credentials import Credentials
from app.routers.smartapi.websockets.smart_websocket import DataWebSocket
from app.utils.urls import NSE_STOCK_SYMBOLS
credentials=Credentials.get_credentials()

action = 0
mode = 3


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
    credentials.api_key,
    credentials.client_id,
    feed_token,
    tokens,
    credentials.correlation_id,
    mode,
)
data_websocket.connect()
data_websocket.send_heart_beat()
