from sqlmodel import SQLModel, Session, delete, select, or_
from app.database.sqlite.models.smartapi_models import SmartAPIToken
from typing import List


def deleted_all_data(session: Session):
    statement = delete(SmartAPIToken)
    session.exec(statement)


def delete_data(data: SmartAPIToken | List[SmartAPIToken], session: Session):
    if isinstance(data, SmartAPIToken):
        data = [data]
    delete()
    session.delete()
    session.commit()
    session.close()


def insert_data(
    data: SmartAPIToken | List[SmartAPIToken],
    session: Session,
    remove_existing: bool = False,
):
    if isinstance(data, SmartAPIToken):
        data = [data]
    if remove_existing:
        deleted_all_data(session)

    session.add_all(data)
    session.commit()
    session.close()


def get_conditions_list(attributes: dict):
    conditions = []
    for key, value in attributes.items():
        if value:
            try:
                conditions.append(getattr(SmartAPIToken, key) == value)
            except AttributeError:
                print(f"Attribute {key} not found in SmartAPIToken model, skipping...")

    return conditions


def get_tokens_data_by_any_condition(
    session: Session,
    **kwargs,
):
    conditions = get_conditions_list(kwargs)

    statement = select(SmartAPIToken).where(or_(*conditions))
    result = session.exec(statement).all()
    return result


def get_tokens_data_by_all_condition(
    session: Session,
    **kwargs,
):
    conditions = get_conditions_list(kwargs)

    statement = select(SmartAPIToken).where(*conditions)
    result = session.exec(statement).all()
    return result
