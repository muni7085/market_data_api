from app.database.sqlite.models.websocket_models import WebsocketLTPData
from app.database.sqlite.sqlite_db_connection import get_session
def save_socket_data_to_db(data:WebsocketLTPData):
    """
    Save the data to the database
    """
    