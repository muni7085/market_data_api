from app.utils.urls import SQLITE_DB_URL
from sqlmodel import create_engine, SQLModel, Session

sqlite_engine = create_engine(SQLITE_DB_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(sqlite_engine)


def get_session():
    with Session(sqlite_engine) as session:
        yield session
