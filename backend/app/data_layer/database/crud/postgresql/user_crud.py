from sqlmodel import select, SQLModel
from app.data_layer.database.models.user_model import User, UserVerification
from app.data_layer.database.db_connections.postgresql import get_session
from typing import Dict, Optional, Type


#### User CRUD operations ####
def check_field_existence(
    model: Type[SQLModel], field_values: Dict[str, str], session=None
) -> Optional[str]:
    """
    Checks if any of the specified fields have values that already exist in the database.

    Parameters:
    ----------
    model: ``Type[SQLModel]``
        The model to check for the existence of the field values
    field_values: ``Dict[str, str]``
        A dictionary containing the field names and values to check for existence
    session: ``Optional[Session]``
        The session to use for the database operations

    Returns:
    -------
    ``Optional[str]``
        A message indicating if any of the field values already exist in the database
    """
    session = session or next(get_session())

    for field_name, value in field_values.items():
        statement = select(model).where(getattr(model, field_name) == value)

        if session.exec(statement).first():
            return f"{field_name.replace('_', ' ').capitalize()} already exists"

    return None


def get_user_by_field(field_name: str, field_value: str):
    with next(get_session()) as session:
        statement = select(User).where(getattr(User, field_name) == field_value)
        result = session.exec(statement).first()

        return result


def create_user(user: User):
    with next(get_session()) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

        return user


def get_user(user_id: str):
    with next(get_session()) as session:
        statement = select(User).where(User.user_id == user_id)
        result = session.exec(statement).first()

        return result


def update_user(user_id: str, user_data: dict):
    with next(get_session()) as session:
        user = get_user(user_id)
        if user:
            for key, value in user_data.items():
                print(f"Key: {key}, Value: {value}")
                setattr(user, key, value)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

        return None


def delete_user(user_id: int):
    with next(get_session()) as session:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            session.commit()
            return True

        return False


#### UserVerification CRUD operations ####


def get_user_verification(recipient: str):
    with next(get_session()) as session:
        statement = select(UserVerification).where(
            UserVerification.recipient == recipient
        )
        result = session.exec(statement).first()

        return result


def create_or_update_user_verification(user_verification: UserVerification):
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
