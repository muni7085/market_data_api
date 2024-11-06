"""
This module contains the CRUD operations for the SocketStockPriceInfo table in the SQLite database.
"""

from pathlib import Path
from typing import Generator, cast

from sqlalchemy.dialects.sqlite import insert
from sqlmodel import Session, select

from app.data_layer.database.models.websocket_model import SocketStockPriceInfo
from app.data_layer.database.crud.sqlite_db_connection import get_session
from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


def upsert(
    stock_price_info: dict[str, str | None] | list[dict[str, str | None]],
    session: Generator[Session, None, None],
):
    """
    Upsert means insert the data into the table if it does not already exist.
    If the data already exists, it will be updated with the new data

    Example:
    --------
    >>> If the table has the following data:
    | id | symbol | price |
    |----|--------|-------|
    | 1  | AAPL   | 100   |
    | 2  | MSFT   | 200   |

    >>> If the following data is upserted:
    | id | symbol | price |
    |----|--------|-------|
    | 1  | AAPL   | 150   |
    | 3  | GOOGL  | 300   |

    >>> The table will be updated as:
    | id | symbol | price |
    |----|--------|-------|
    | 1  | AAPL   | 150   |
    | 2  | MSFT   | 200   |
    | 3  | GOOGL  | 300   |

    Parameters
    ----------
    stock_price_info: ``dict[str, str|None]| list[dict[str, str|None]]``
        The SocketStockPriceInfo objects to upsert into the table
    session: ``Generator[Session, None, None]``
        The SQLModel session object to use for the database operations
    """
    upsert_stmt = insert(SocketStockPriceInfo).values(stock_price_info)

    # Create a dictionary of columns to update if the data already exists
    columns = {
        column.name: getattr(upsert_stmt.excluded, column.name)
        for column in upsert_stmt.excluded
    }
    upsert_stmt = upsert_stmt.on_conflict_do_update(set_=columns)

    with next(session) as db_session:
        db_session.exec(upsert_stmt)  # type: ignore
        db_session.commit()


def insert_or_ignore(
    stock_price_info: dict[str, str | None] | list[dict[str, str | None]],
    session: Generator[Session, None, None],
):
    """
    Add the provided data into the StockPriceInfo table if the data does not already exist.
    If the data already exists, it will be ignored.

    Parameters
    ----------
    stock_price_info: ``dict[str, str|None]| list[dict[str, str|None]]``
        The SocketStockPriceInfo objects to insert into the table
    session: ``Generator[Session, None, None]``
        The SQLModel session object to use for the database operations
    """
    insert_stmt = insert(SocketStockPriceInfo).values(stock_price_info)
    insert_stmt = insert_stmt.on_conflict_do_nothing()

    with next(session) as db_session:
        db_session.exec(insert_stmt)  # type: ignore
        db_session.commit()


def insert_data(
    data: (
        SocketStockPriceInfo
        | dict[str, str | None]
        | list[SocketStockPriceInfo | dict[str, str | None]]
        | None
    ),
    update_existing: bool = False,
    session: Generator[Session, None, None] | None = None,
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
    update_existing: ``bool``, ( defaults = False )
        If True, the existing data in the table will be updated with the new data
    session: ``Generator[Session, None, None]``, ( defaults = None )
        The SQLModel session object to use for the database operations. If not provided,
        a new session will be created from the database connection pool
    """
    if not data:
        logger.warning("Provided data is empty. Skipping insertion.")
        return

    if isinstance(data, (SocketStockPriceInfo, dict)):
        data = [data]

    if not session:
        session = get_session()

    # Convert list of SocketStockPriceInfo to a list of dicts
    data_to_insert = cast(
        list[dict[str, str | None]],
        [
            item.to_dict() if isinstance(item, SocketStockPriceInfo) else item
            for item in data
        ],
    )

    if update_existing:
        upsert(data_to_insert, session)
    else:
        insert_or_ignore(data_to_insert, session)


def get_all_stock_price_info(
    session: Generator[Session, None, None]
) -> list[SocketStockPriceInfo]:
    """
    Retrieve all the data from the SocketStockPriceInfo table in the SQLite database.

    Parameters
    ----------
    session: ``Generator[Session, None, None]``
        The SQLModel session object to use for the database operations

    Returns
    -------
    ``List[SocketStockPriceInfo]``
        The list of all the SocketStockPriceInfo objects present in the table
    """
    with next(session) as db_session:
        stmt = select(SocketStockPriceInfo)
        return db_session.exec(stmt).all()  # type: ignore
