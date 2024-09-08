from app.database.sqlite.crud.smartapi_curd import insert_data
from app.database.sqlite.sqlite_db_connection import create_db_and_tables
from app.utils.fetch_data import fetch_data
from app.utils.smartapi.data_processor import process_token_data
from app.utils.smartapi.urls import SMARTAPI_TOKENS_URL
from app.utils.urls import SQLITE_DB_URL
from pathlib import Path


def create_smartapi_tokens_db(remove_existing: bool = True):
    """
    Creates the SmartAPI tokens database and tables if they do not exist.
    """
    print(f"Checking if database exists at {SQLITE_DB_URL.split('sqlite:///')[-1]} {Path(SQLITE_DB_URL.split('sqlite:///')[-1]).exists()}")
    if Path(SQLITE_DB_URL.split("sqlite:///")[-1]).exists():
        return None
    
    create_db_and_tables()
    tokens_data = fetch_data(SMARTAPI_TOKENS_URL)
    processed_data = process_token_data(tokens_data)
    print(f"Removing existing data from SmartAPIToken table... {remove_existing}")
    insert_data(processed_data, remove_existing=remove_existing)
