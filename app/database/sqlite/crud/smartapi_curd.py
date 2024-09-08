"""
This script contains the CRUD operations for the SmartAPIToken table.
"""

from typing import Dict, List, Sequence

from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import delete, or_, select
from app.database.sqlite.sqlite_db_connection import get_session
from app.utils.common.logger_utils import get_logger

from app.database.sqlite.models.smartapi_models import SmartAPIToken

from pathlib import Path

logger = get_logger(Path(__file__).name)


def deleted_all_data():
    """
    Deletes all data from the SmartAPIToken table.
    """
    with next(get_session()) as session:
        statement = delete(SmartAPIToken)
        session.exec(statement)


def insert_data(
    data: SmartAPIToken | List[SmartAPIToken],
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
        logger.warning(f"Removing existing data from SmartAPIToken table...")
        deleted_all_data()

    with next(get_session()) as session:
        session.add_all(data)
        session.commit()
        session.close()


def get_conditions_list(condition_attributes: Dict[str, str]) -> List[BinaryExpression]:
    """
    Generate a list of conditions based on the provided attributes.

    This function takes a dictionary of attributes and their corresponding values as input.
    It generates a list of SQLAlchemy BinaryExpression objects, which can be used as conditions
    in a database query.

    Parameters
    ----------
    condition_attributes: ``Dict[str, str]``
        A dictionary of attributes and their corresponding values.

    Returns
    -------
    conditions: ``List[BinaryExpression]``
        A list of SQLAlchemy BinaryExpression objects.
    """
    conditions = []

    for key, value in condition_attributes.items():
        if value:
            try:
                conditions.append(getattr(SmartAPIToken, key) == value)
            except AttributeError:
                print(f"Attribute {key} not found in SmartAPIToken model, skipping...")

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
        The attributes should be the columns of the SmartAPIToken model.

    Returns
    -------
    result: ``List[SmartAPIToken]``
        A list of SmartAPIToken objects that match the any of the specified conditions.
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
        The attributes should be the columns of the SmartAPIToken model.

    Returns
    -------
    result: ``List[SmartAPIToken]``
        A list of SmartAPIToken objects that match the all of the specified conditions.
    """
    with next(get_session()) as session:
        conditions = get_conditions_list(kwargs)
        statement = select(SmartAPIToken).where(*conditions)
        result = session.exec(statement).all()

    return result
