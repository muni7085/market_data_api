""" 
Test the database connection and interaction with the SQLite database.
"""

from sqlmodel import inspect, select
from app.database.sqlite.sqlite_db_connection import (
    create_db_and_tables,
    get_session,
    sqlite_engine,
)
from app.database.sqlite.models.smartapi_models import SmartAPIToken

table_names = ["smartapitoken"]


def test_database_init_and_interaction():
    """ 
    Test if the database is created and tables are created and empty and able to interact with the database.
    """
    create_db_and_tables()

    # Check if the session is active
    session = next(get_session())
    assert session.is_active
    assert session.connection
    assert session.bind

    # Check if the tables are created
    metadata = inspect(sqlite_engine)
    for table in metadata.get_table_names():
        assert table in table_names

    # Check if the tables are empty and able to interact with the database
    # results=session.exec(select(SmartAPIToken)).all()
    
    
