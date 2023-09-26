from data_provider.smart_api.constants import API_KEY, CLIENT_ID, PWD, TOKEN
from SmartApi import SmartConnect
import pyotp


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
