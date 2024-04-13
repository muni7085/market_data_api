import http.client
from http.client import HTTPConnection
from typing import Dict, Optional, Union

import pyotp
from SmartApi import SmartConnect

from app.utils.common.types.reques_types import RequestType
from app.utils.smartapi.credentials import Credentials


class Singleton(type):
    """
    Singleton class to create a single instance of the SmartApiConnection class.
    """

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SmartApiConnection(metaclass=Singleton):
    """
    SmartApiConnection class to create a connection to the SmartAPI.

    Attributes:
    -----------
    credentials: ``Credentials``
        The credentials object to authenticate the connection.
    api: ``SmartConnect``
        The SmartConnect object to connect to the SmartAPI.
    data: ``dict``
        The data object to store the session data like jwtToken.
    """

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.api = SmartConnect(self.credentials.api_key)
        totp = pyotp.TOTP(self.credentials.token).now()
        self.data = self.api.generateSession(
            self.credentials.client_id, self.credentials.pwd, totp
        )

    def get_auth_token(self) -> Optional[str]:
        """
        The method to get the authentication token from the session data.

        Returns:
        --------
        ``Optional[str]``:
            The authentication token if present, else None.
        """
        if "data" in self.data:
            client_data = self.data["data"]
            if "jwtToken" in client_data:
                return client_data["jwtToken"]
        return None

    def get_headers(self) -> Dict[str, Optional[str]]:
        """
        The method to get the headers for the API request.

        Returns:
        --------
        ``dict``:
            The headers for the API request for the SmartAPI.
        """
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
        """
        Initialze the SmartApiConnection
        """
        credentials = Credentials.get_credentials()
        connection = SmartApiConnection(credentials)
        return connection


def get_endpoint_connection(
    payload: Union[str, dict], request_method_type: RequestType, url: str
) -> HTTPConnection:
    """
    Get the HTTP connection object for making API requests to a specific endpoint to the SmartAPI with the given payload.

    Parameters:
    -----------
    payload: ``Union[str, dict]``
        The payload to be sent in the API request.
    method_type: ``RequestType``
        The request method type like GET, POST, PUT, DELETE from the RequestType enum.\
        eg: RequestType.GET, RequestType.POST
    url: ``str``
        The URL of the endpoint to connect to.
    
    Returns:
    --------
    ``HTTPConnection``:
        The HTTP connection object for the given endpoint.
    

    """
    api_connection = SmartApiConnection.get_connection()
    connection = http.client.HTTPSConnection("apiconnect.angelbroking.com")
    headers = api_connection.get_headers()
    connection.request(request_method_type.value, url, body=payload, headers=headers)

    return connection
