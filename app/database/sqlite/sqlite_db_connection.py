""" This script is responsible for creating a connection to the SQLite database. 
It also provides a function to create the database and tables and a function to 
get a session object to interact with the database."""

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.utils.urls import SQLITE_DB_URL

sqlite_engine = create_engine(SQLITE_DB_URL, echo=True)


def create_db_and_tables():
    """
    Creates the database and tables if they do not exist.
    """
    print(f"db path : {SQLITE_DB_URL}")
    print(f"sqlite_engine : {sqlite_engine}")
    SQLModel.metadata.create_all(sqlite_engine)


def get_session() -> Generator[Session, None, None]:
    """
    Yields a session object to interact with the database.
    """
    with Session(sqlite_engine) as session:
        yield session
