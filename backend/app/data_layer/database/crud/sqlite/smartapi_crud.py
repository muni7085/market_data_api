"""
This script contains the CRUD operations for the SmartAPIToken table.
"""

from pathlib import Path
from typing import Sequence

from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import delete, or_, select

from app.data_layer.database.db_connections.sqlite import get_session
from app.data_layer.database.models.smartapi_model import SmartAPIToken
from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


def deleted_all_data():
    """
    Deletes all data from the SmartAPIToken table.
    """
    with next(get_session()) as session:
        statement = delete(SmartAPIToken)
        session.exec(statement)
        session.commit()


def insert_data(
    data: SmartAPIToken | list[SmartAPIToken],
    remove_existing: bool = False,
):
    """
    Inserts data into the SmartAPIToken table.

    Parameters
    ----------
    data: ``SmartAPIToken`` | ``List[SmartAPIToken]``
        The data to insert into the table.
    remove_existing: ``bool``
        If True, all existing data in the table will be deleted before inserting the new data.
    """
    if isinstance(data, SmartAPIToken):
        data = [data]

    if remove_existing:
        logger.warning("Removing existing data from SmartAPIToken table...")
        deleted_all_data()

    with next(get_session()) as session:
        session.add_all(data)
        session.commit()
        session.close()


def get_conditions_list(condition_attributes: dict[str, str]) -> list[BinaryExpression]:
    """
    Generate a list of conditions based on the provided attributes.

    This function takes a dictionary of attributes and their corresponding values as input.
    It generates a list of SQLAlchemy BinaryExpression objects, which can be used as conditions
    in a database query.

    Parameters
    ----------
    condition_attributes: ``dict[str, str]``
        A dictionary of attributes and their corresponding values

    Returns
    -------
    conditions: ``list[BinaryExpression]``
        A list of SQLAlchemy BinaryExpression objects
    """
    conditions = []

    for key, value in condition_attributes.items():
        if value:
            try:
                conditions.append(getattr(SmartAPIToken, key) == value)
            except AttributeError:
                logger.exception(
                    "Attribute %s not found in SmartAPIToken model, skipping...", key
                )

    return conditions


def get_smartapi_tokens_by_any_condition(**kwargs) -> Sequence[SmartAPIToken]:
    """
    Retrieve a list of SmartAPIToken objects based on the specified conditions.
    The possible keyword arguments are the attributes of the SmartAPIToken model.
    The function returns a list of SmartAPIToken objects that match any of the
    specified conditions. Refer SmartAPIToken model for the attributes.

    Parameters
    ----------
    **kwargs: ``Dict[str, str]``
        The attributes and their corresponding values to filter the data.
        The attributes should be the columns of the SmartAPIToken model

    Returns
    -------
    result: ``List[SmartAPIToken]``
        A list of SmartAPIToken objects that match the any of the specified conditions

    >>> Example:
    >>> get_smartapi_tokens_by_any_condition(symbol="INFY", exchange="NSE")
    >>> [SmartAPIToken(symbol='INFY', exchange='NSE', token='1224', ...),
            SmartAPIToken(symbol='TCS', exchange='NSE', token='1225', ...), ...]

    The above example will return all the SmartAPIToken objects with symbol 'INFY' or
    exchange 'NSE'.
    """
    with next(get_session()) as session:
        conditions = get_conditions_list(kwargs)

        statement = select(SmartAPIToken).where(
            or_(*conditions)  # pylint: disable=no-value-for-parameter
        )
        result = session.exec(statement).all()

        return result


def get_smartapi_tokens_by_all_conditions(
    **kwargs,
) -> Sequence[SmartAPIToken]:
    """
    Retrieve a list of SmartAPIToken objects based on the specified conditions.
    The possible keyword arguments are the attributes of the SmartAPIToken model.
    The function returns a list of SmartAPIToken objects that match all of the
    specified conditions. Refer SmartAPIToken model for the attributes.

    Parameters
    ----------
    **kwargs: ``Dict[str, str]``
        The attributes and their corresponding values to filter the data.
        The attributes should be the columns of the SmartAPIToken model

    Returns
    -------
    result: ``List[SmartAPIToken]``
        A list of SmartAPIToken objects that match the all of the specified conditions

    >>> Example:
    >>> get_smartapi_tokens_by_all_conditions(symbol="INFY", exchange="NSE")
    >>> [SmartAPIToken(symbol='INFY', exchange='NSE', token='1224', ...)]

    The above example will return all the SmartAPIToken objects with symbol 'INFY' and
    exchange 'NSE'.
    """
    with next(get_session()) as session:
        conditions = get_conditions_list(kwargs)
        statement = select(SmartAPIToken).where(*conditions)
        result = session.exec(statement).all()

    return result
