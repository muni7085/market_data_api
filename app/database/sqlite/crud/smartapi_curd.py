"""
This script contains the CRUD operations for the SmartAPIToken table.
"""

from typing import Dict, List, Sequence

from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import Session, delete, or_, select

from app.database.sqlite.models.smartapi_models import SmartAPIToken


def deleted_all_data(session: Session):
    """
    Deletes all data from the SmartAPIToken table.

    Parameters
    ----------
    session: ``Session``
        The session object to interact with the database.

    """
    statement = delete(SmartAPIToken)
    session.exec(statement)


def insert_data(
    data: SmartAPIToken | List[SmartAPIToken],
    session: Session,
    remove_existing: bool = False,
):
    """
    Inserts data into the SmartAPIToken table.

    Parameters
    ----------
    data: ``SmartAPIToken`` | ``List[SmartAPIToken]``
        The data to insert into the table.
    session: ``Session``
        The session object to interact with the database.
    remove_existing: ``bool``
        If True, all existing data in the table will be deleted before inserting the new data.
    """
    if isinstance(data, SmartAPIToken):
        data = [data]
    if remove_existing:
        deleted_all_data(session)

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


def get_smartapi_tokens_by_any_condition(
    session: Session, **kwargs
) -> Sequence[SmartAPIToken]:
    """
    Retrieve a list of SmartAPIToken objects based on the specified conditions.
    The possible keyword arguments are the attributes of the SmartAPIToken model.
    The function returns a list of SmartAPIToken objects that match any of the specified conditions.
    Refer SmartAPIToken model for the attributes.

    Parameters
    ----------
    sesssion: ``Session``
        The session object to interact with the database.
    **kwargs: ``Dict[str, str]``
        The attributes and their corresponding values to filter the data.
        The attributes should be the columns of the SmartAPIToken model.

    Returns
    -------
    result: ``List[SmartAPIToken]``
        A list of SmartAPIToken objects that match the any of the specified conditions.
    """
    conditions = get_conditions_list(kwargs)

    statement = select(SmartAPIToken).where(
        or_(*conditions)  # pylint: disable=no-value-for-parameter
    )
    result = session.exec(statement).all()
    return result


def get_smartapi_tokens_by_all_conditions(
    session: Session,
    **kwargs,
) -> Sequence[SmartAPIToken]:
    """
    Retrieve a list of SmartAPIToken objects based on the specified conditions.
    The possible keyword arguments are the attributes of the SmartAPIToken model.
    The function returns a list of SmartAPIToken objects that match all of the specified conditions.
    Refer SmartAPIToken model for the attributes.

    Parameters
    ----------
    sesssion: ``Session``
        The session object to interact with the database.
    **kwargs: ``Dict[str, str]``
        The attributes and their corresponding values to filter the data.
        The attributes should be the columns of the SmartAPIToken model.

    Returns
    -------
    result: ``List[SmartAPIToken]``
        A list of SmartAPIToken objects that match the all of the specified conditions.
    """
    conditions = get_conditions_list(kwargs)

    statement = select(SmartAPIToken).where(*conditions)
    result = session.exec(statement).all()
    return result
