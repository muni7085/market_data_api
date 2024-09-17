from typing import List

from sqlmodel import select

from app.database.sqlite.models.websocket_models import SocketStockPriceInfo
from app.database.sqlite.sqlite_db_connection import get_session


def insert_stock_price_info_objects(stocks_price_info: List[SocketStockPriceInfo]):
    
    with next(get_session()) as session:
        session.bulk_save_objects(stocks_price_info)
        session.commit()
    
def get_stock_price_info(token: str,retrieval_timestamp) -> SocketStockPriceInfo:
    with next(get_session()) as session:
        stmt=select(SocketStockPriceInfo).where(SocketStockPriceInfo.token == token,SocketStockPriceInfo.retrieval_timestamp == retrieval_timestamp)
        result=session.exec(stmt)
        return result.one()

def insert_data(data: SocketStockPriceInfo | List[SocketStockPriceInfo]):
    """
    Insert the provided data into the SocketStockPriceInfo table in the SQLite database.

    Parameters
    ----------
    data: ``SocketStockPriceInfo`` | ``List[SocketStockPriceInfo]``
        The data to insert.
    """
    if isinstance(data, SocketStockPriceInfo):
        data = [data]
    insert_stock_price_info_objects(data)
