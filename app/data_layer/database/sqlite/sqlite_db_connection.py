""" 
This script is responsible for creating a connection to the SQLite database. 
It also provides a function to create the database and tables and a function
to get a session object to interact with the database.
"""

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.engine import Engine

from app.utils.urls import SQLITE_DB_URL

sqlite_engine = create_engine(SQLITE_DB_URL, echo=True)

def create_sqlite_engine(sqlite_db_url: str=None) -> Engine:
    """
    Creates and returns a SQLite engine object.
    """
    return create_engine(sqlite_db_url)


def create_db_and_tables(engine: Engine = None) -> None:
    """
    Creates the database and tables if they do not exist.
    """
    if engine is None:
        engine = sqlite_engine

    SQLModel.metadata.create_all(engine)


def get_session(engine:Engine) -> Generator[Session, None, None]:
    """
    Yields a session object to interact with the database.
    """
    if engine is None:
        engine = sqlite_engine
    
    with Session(sqlite_engine) as session:
        yield session
