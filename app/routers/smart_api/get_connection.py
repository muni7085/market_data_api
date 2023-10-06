import pyotp
from SmartApi import SmartConnect, smartWebSocketV2

from app.routers.smart_api.utils.credentails import Credentials


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SmartApiConnection(metaclass=Singleton):
    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.api = SmartConnect(self.credentials.api_key)
        totp = pyotp.TOTP(self.credentials.token).now()
        self.data = self.api.generateSession(
            self.credentials.client_id, self.credentials.pwd, totp
        )

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
            "X-PrivateKey": self.credentials.api_key,
        }
        return headers

    @staticmethod
    def get_connection():
        credentials = Credentials.get_credentials()
        connection = SmartApiConnection(credentials)
        return connection
