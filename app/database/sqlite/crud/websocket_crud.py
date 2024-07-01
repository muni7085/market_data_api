from app.database.sqlite.models.websocket_models import WebsocketLTPData
from typing import List

from sqlmodel import Session


def insert_socket_data_to_db(
    data: WebsocketLTPData | List[WebsocketLTPData], session: Session
):
    """
    Insert the provided data into `websocketltpdata` table in the database.

    Parameters
    ----------
    data: ``WebsocketLTPData`` | ``List[WebsocketLTPData]``
        The data to insert into the table.
    session: ``Session``
        The session object to interact with the database.
    """
    if isinstance(data, WebsocketLTPData):
        data = [data]

    session.add_all(data)
    session.commit()
    session.close()
