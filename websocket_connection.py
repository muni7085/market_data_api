from app.routers.smart_api.get_connection import SmartApiConnection
from app.routers.smart_api.utils.constants import API_KEY, CLIENT_ID
from app.routers.smart_api.websocket_call_backs import DataWebSocket

action = 0
mode = 2
correlation_id = "abc123"

tokens = [
    {
        "exchangeType": 1,
        "tokens": [
            "11377",
            "2643",
            "8050",
            "10604",
            "3757",
            "6596",
            "28859",
            "14687",
            "592",
            "17659",
        ],
    }
]
smart_api_connection = SmartApiConnection.get_connection()
auth_token = smart_api_connection.get_auth_token()
feed_token = smart_api_connection.api.getfeedToken()
data_websocket = DataWebSocket(
    auth_token, API_KEY, CLIENT_ID, feed_token, tokens, correlation_id, mode
)
data_websocket.connect()
