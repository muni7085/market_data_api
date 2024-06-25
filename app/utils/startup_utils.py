from app.database.sqlite.sqlite_db_connection import create_db_and_tables, get_session
from app.utils.fetch_data import fetch_data
from app.utils.smartapi.data_processor import process_token_data
from app.utils.smartapi.urls import SMARTAPI_TOKENS_URL
from app.database.sqlite.crud.smartapi_curd import insert_data


def create_smartapi_tokens_db():
    create_db_and_tables()
    tokens_data = fetch_data(SMARTAPI_TOKENS_URL)
    processed_data = process_token_data(tokens_data)
    insert_data(processed_data, next(get_session()), remove_existing=True)
