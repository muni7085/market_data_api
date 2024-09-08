from typing import List

from app.database.sqlite.models.websocket_models import SocketStockPriceInfo
from app.database.sqlite.sqlite_db_connection import get_session


def insert_data(data: SocketStockPriceInfo | List[SocketStockPriceInfo]):
    """
    Insert the provided data into the SocketStockPriceInfo table in the SQLite database.

    Parameters
    ----------
    data: ``SocketStockPriceInfo`` | ``List[SocketStockPriceInfo]``
        The data to insert.
    """
    with next(get_session()) as session:
        if isinstance(data, SocketStockPriceInfo):
            data = [data]

        session.add_all(data)
        session.commit()
        session.close()
