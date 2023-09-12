from fetch_data.constants import API_KEY, CLIENT_ID, PWD, TOKEN
from smartapi import SmartConnect
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
