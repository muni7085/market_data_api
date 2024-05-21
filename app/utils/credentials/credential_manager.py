from app.utils.credentials.credentials import Credentials


def get_credentials(credentials_name: str):
    credentials = Credentials.by_name(credentials_name)
    return credentials.get_credentials()
