import pyotp
from SmartApi import SmartConnect, smartWebSocketV2

from app.routers.smart_api.utils.constants import (API_KEY, CLIENT_ID, PWD,
                                                    TOKEN)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SmartApiConnection(metaclass=Singleton):
    def __init__(self):
        self.api = SmartConnect(API_KEY)
        totp = pyotp.TOTP(TOKEN).now()
        self.data = self.api.generateSession(CLIENT_ID, PWD, totp)

    def get_auth_token(self):
        if "data" in self.data:
            client_data = self.data["data"]
            if "jwtToken" in client_data:
                return client_data["jwtToken"]
        return None

    def get_headers(self):
        auth_token = self.get_auth_token()
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "CLIENT_LOCAL_IP",
            "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
            "X-MACAddress": "MAC_ADDRESS",
            "X-PrivateKey": API_KEY,
        }
        return headers

    @staticmethod
    def get_connection():
        connection = SmartApiConnection()
        return connection


def get_smart_websocket_connection():
    smart_api_connection = SmartApiConnection.get_connection()
    auth_token = smart_api_connection.get_auth_token()
    feed_token = smart_api_connection.data.getfeedToken()
    return smartWebSocketV2(auth_token, API_KEY, CLIENT_ID, feed_token)
