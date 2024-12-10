from pathlib import Path
from typing import Dict, Type

from sqlmodel import Session, SQLModel, select

from app.data_layer.database.db_connections.postgresql import get_session
from app.data_layer.database.models.user_model import User, UserVerification
from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


#### User CRUD operations ####
def is_attr_data_in_db(
    model: Type[SQLModel], att_values: Dict[str, str], session: Session | None = None
) -> dict | None:
    """
    Checks if any of the specified fields have values that already exist in the database.

    For example, if the `att_values` dictionary contains the key-value pair
    {"email": "example@gmail.com"}, this function will check if there is any
    user in the database with the email "example@gmail.com" and return a message
    indicating that the email already exists.

    Parameters:
    ----------
    model: ``Type[SQLModel]``
        The model to check for the existence of the field values
    att_values: ``Dict[str, str]``
        A dictionary containing the field names and values to check for existence
    session: ``Session | None``, ( default = None )
        The session to use for the database operations

    Returns:
    -------
    ``str | None``
        A message indicating that the field already exists if found, otherwise None
    """
    session = session or next(get_session())

    existing_attr: dict | None = None

    for attr_name, attr_value in att_values.items():
        statement = select(model).where(getattr(model, attr_name) == attr_value)

        if session.exec(statement).first():
            existing_attr = {"message": f"{attr_name} already exists"}
            break

    return existing_attr


def get_user_by_attr(attr_name: str, attr_value: str) -> User | None:
    """
    Retrieves a user from the database using the specified attribute name and value.
    Example: get_user_by_attr("email", "example@gmail.com")

    Parameters:
    ----------
    attr_name: ``str``
        The name of the attribute used to query the database
    attr_value: ``str``
        Value of the attribute to match against the database

    Returns:
    -------
    ``User | None``
        The user object if found, otherwise None
    """

    with next(get_session()) as session:
        statement = select(User).where(getattr(User, attr_name) == attr_value)
        result = session.exec(statement).first()

        return result


def create_user(user: User) -> bool:
    """
    Adds a new user to the database.

    Parameters:
    ----------
    user: ``User``
        The user object to add to the database

    Returns:
    -------
    ``bool``
        True if the user was created successfully, otherwise False
    """
    try:
        with next(get_session()) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

        return True
    except Exception as e:
        logger.error("Error creating user: %s", e)

        return False


def get_user(user_id: int):
    """
    Retrieve a user from the database using the user_id.

    Parameters:
    ----------
    user_id: ``int``
        The `user_id` of the user to retrieve

    Returns:
    -------
    ``User``
        The user object if found, otherwise None
    """
    with next(get_session()) as session:
        statement = select(User).where(User.user_id == user_id)
        result = session.exec(statement).first()

        return result


def update_user(user_id: int, user_data: dict) -> User | None:
    """
    Update the fields of a user in the database using the `user_id` if the user
    present in the database. The `user_data` dictionary should contain the fields
    to update and their new values.

    Parameters:
    ----------
    user_id: ``int``
        The `user_id` of the user to update
    user_data: ``dict``
        A dictionary containing the fields to update and their new values

    Returns:
    -------
    ``User | None``
        The updated user object if the user was updated successfully, otherwise None


    >>> Example:
        update_user("1234", {"first_name": "John", "last_name": "Doe"})
    """
    with next(get_session()) as session:
        user = get_user(user_id)

        if user:
            for key, value in user_data.items():
                setattr(user, key, value)

            session.add(user)
            session.commit()
            session.refresh(user)

        return user


def delete_user(user_id: str) -> bool:
    """
    Delete a user from the database using the `user_id` if the user is present.

    Parameters:
    ----------
    user_id: ``str``
        The `user_id` of the user to delete

    Returns:
    -------
    ``bool``
        True if the user was deleted successfully, otherwise False
    """
    with next(get_session()) as session:
        user = session.get(User, user_id)

        if user:
            session.delete(user)
            session.commit()

        return bool(user)


#### UserVerification CRUD operations ####


def get_user_verification(recipient: str) -> UserVerification | None:
    """
    Retrieve a user verification object from the database using the recipient (email/phone number).

    Parameters:
    ----------
    recipient: ``str``
        The email or phone number of the user to retrieve the verification object

    Returns:
    -------
    ``UserVerification | None``
        The user verification object if found, otherwise None
    """
    with next(get_session()) as session:
        statement = select(UserVerification).where(
            UserVerification.recipient == recipient
        )
        result = session.exec(statement).first()

        return result


def create_or_update_user_verification(user_verification: UserVerification):
    """
    Create a new user verification object in the database if it does not exist, otherwise
    update the existing object. If the user verification object already exists, the function
    will update the verification code, expiration time, reverified datetime, and verification
    medium.

    Parameters:
    ----------
    user_verification: ``UserVerification``
        The user verification object to add or update in the database
    """
    with next(get_session()) as session:
        existing_user_verification = get_user_verification(user_verification.recipient)

        if not existing_user_verification:
            existing_user_verification = user_verification
        else:
            existing_user_verification.verification_code = (
                user_verification.verification_code
            )
            existing_user_verification.expiration_time = (
                user_verification.expiration_time
            )
            existing_user_verification.reverified_datetime = (
                user_verification.reverified_datetime
            )
            existing_user_verification.verification_medium = (
                user_verification.verification_medium
            )

        session.add(existing_user_verification)
        session.commit()
        session.refresh(existing_user_verification)
