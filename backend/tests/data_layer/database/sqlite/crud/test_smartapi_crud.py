"""" 
This module contains tests for the smartapi_crud.py module in the sqlite/crud directory.
"""

from pathlib import Path

import pytest
from app.data_layer.database.crud.sqlite.smartapi_crud import (
    get_smartapi_tokens_by_all_conditions,
    get_smartapi_tokens_by_any_condition,
)
from app.data_layer.database.db_connections.sqlite import get_session, sqlite_engine
from app.data_layer.database.models.smartapi_model import SmartAPIToken
from app.utils.startup_utils import create_smartapi_tokens_db
from app.utils.urls import SQLITE_DB_URL


@pytest.fixture
def session():
    """
    Fixture to get the session object.
    """
    return next(get_session())


def test_get_smartapi_tokens_by_any_and_all_condition():
    """
    Test the get_smartapi_tokens_by_any_condition
    """

    db_file_path = Path(SQLITE_DB_URL.split("sqlite:///")[-1])
    remove_at_end = not db_file_path.exists()

    try:
        create_smartapi_tokens_db(True)

        # Insert test data
        token1 = SmartAPIToken(
            token="1594",
            symbol="INFY",
            name="INFY",
            instrument_type="EQ",
            exchange="NSE",
            expiry_date="",
            strike_price=-1.0,
            tick_size=5.0,
            lot_size=1,
        )

        result = get_smartapi_tokens_by_any_condition(symbol="INFY")
        for item in result:
            assert "INFY" == item.symbol

        result = get_smartapi_tokens_by_any_condition(exchange="BSE")
        for item in result:
            assert "BSE" == item.exchange

        result = get_smartapi_tokens_by_all_conditions(symbol="INFY", exchange="NSE")
        assert token1.to_dict() == result[1].to_dict()

        result = get_smartapi_tokens_by_all_conditions(symbol="SBI", exchange="BSE")
        for item in result:
            assert "SBI" == item.symbol
            assert "BSE" == item.exchange

    finally:
        sqlite_engine.dispose()

        if remove_at_end:
            db_file_path.unlink()
