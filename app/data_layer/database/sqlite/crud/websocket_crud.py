"""
This module contains the CRUD operations for the SocketStockPriceInfo table in the SQLite database.
"""

from pathlib import Path
from typing import cast

from sqlalchemy.dialects.sqlite import insert

from app.data_layer.database.sqlite.models.websocket_models import SocketStockPriceInfo
from app.data_layer.database.sqlite.sqlite_db_connection import get_session
from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


def upsert(stock_price_info: dict[str, str | None] | list[dict[str, str | None]]):
    """
    Upsert means insert the data into the table if it does not already exist.
    If the data already exists, it will be updated with the new data

    Parameters
    ----------
    stock_price_info: ``dict[str, str|None]| list[dict[str, str|None]]``
        The SocketStockPriceInfo objects to upsert into the table
    """
    upsert_stmt = insert(SocketStockPriceInfo).values(stock_price_info)
    columns = {
        column.name: getattr(upsert_stmt.excluded, column.name)
        for column in upsert_stmt.excluded
    }
    upsert_stmt = upsert_stmt.on_conflict_do_update(set_=columns)

    with next(get_session()) as session:
        session.exec(upsert_stmt)  # type: ignore
        session.commit()


def insert_or_ignore(
    stock_price_info: dict[str, str | None] | list[dict[str, str | None]]
):
    """
    Add the provided data into the StockPriceInfo table if the data does not already exist.
    If the data already exists, it will be ignored.

    Parameters
    ----------
    stock_price_info: ``dict[str, str|None]| list[dict[str, str|None]]``
        The SocketStockPriceInfo objects to insert into the table
    """
    insert_stmt = insert(SocketStockPriceInfo).values(stock_price_info)
    insert_stmt = insert_stmt.on_conflict_do_nothing()

    with next(get_session()) as session:
        session.exec(insert_stmt)  # type: ignore
        session.commit()


def insert_data(
    data: (
        SocketStockPriceInfo
        | dict[str, str | None]
        | list[SocketStockPriceInfo | dict[str, str | None]]
        | None
    ),
    update_existing: bool = False,
):
    """
    Insert the provided data into the SocketStockPriceInfo table in the SQLite database. It
    will handle both single and multiple data objects. If the data already exists in the table,
    it will either update the existing data or ignore the new data based on the value of the
    `update_existing` parameter

    Parameters
    ----------
    data: ``SocketStockPriceInfo | dict[str, str|None] | List[SocketStockPriceInfo | dict[str, str | None]] | None``
        The data to insert into the table
    update_existing: ``bool``
        If True, the existing data in the table will be updated with the new data.
    """
    # Check if data is None or empty
    if not data:
        logger.warning("Provided data is empty. Skipping insertion.")
        return

    # Convert single item to a list
    if isinstance(data, (SocketStockPriceInfo, dict)):
        data = [data]

    # Convert list of SocketStockPriceInfo to a list of dicts
    data_to_insert = cast(
        list[dict[str, str | None]],
        [
            item.to_dict() if isinstance(item, SocketStockPriceInfo) else item
            for item in data
        ],
    )

    # Handle upsert or insert
    if update_existing:
        upsert(data_to_insert)
    else:
        insert_or_ignore(data_to_insert)
