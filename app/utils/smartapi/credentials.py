# pylint: disable=too-many-arguments
import os

from app.utils.common.exceptions import CredentialsException
from app.utils.file_utils import load_json_data
from app.utils.smartapi.constants import SMART_API_CREDENTIALS


class Credentials:
    """
    Credentials class to store the credentials required to authenticate the SmartAPI connection.

    Attributes:
    -----------
    api_key: ``str``
        The API key that is generated from the SmartAPI website.
    client_id: ``str``
        The client id is the Angel Broking client id.
    pwd: ``str``
        The password is the Angel Broking login password or pin.
    token: ``str``
        The token is the client secret token generated from the SmartAPI website.
    correlation_id: ``str``
        The correlation id is the unique id to identify the request.

    """

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
        """
        Create a Credentials object from the credentials file.

        Raises:
        -------
        ``CredentialsException``
            If the credentials file path is not set in the environment variable.

        Returns:
        --------
        ``Credentials``
            The credentials object with the API key, client id, password, token and correlation id.
        """
        credentials_path = os.getenv(SMART_API_CREDENTIALS)

        if not credentials_path:
            raise CredentialsException(SMART_API_CREDENTIALS)

        credentials = load_json_data(credentials_path)
        return Credentials(**credentials)
