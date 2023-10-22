import os
from app.utils.file_utils import load_json_data


class Credentials:
    def __init__(
        self, api_key: str, client_id: str, pwd: str, token: str, correlation_id: str
    ) -> None:
        self.api_key = api_key
        self.client_id = client_id
        self.pwd = pwd
        self.token = token
        self.correlation_id = correlation_id

    @staticmethod
    def get_credentials():
        credentials_path = os.environ["SMARTAPI_CREDENTIALS"]
        credentials = load_json_data(credentials_path)
        return Credentials(**credentials)
