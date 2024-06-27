"""" 
This module contains tests for the smartapi_crud.py module in the sqlite/crud directory.
"""

from pathlib import Path

import pytest

from app.database.sqlite.crud.smartapi_curd import (
    get_smartapi_tokens_by_all_conditions,
    get_smartapi_tokens_by_any_condition,
)
from app.database.sqlite.models.smartapi_models import SmartAPIToken
from app.database.sqlite.sqlite_db_connection import get_session
from app.utils.startup_utils import create_smartapi_tokens_db
from app.utils.urls import SQLITE_DB_URL


@pytest.fixture
def session():
    """
    Fixture to get the session object.
    """
    return next(get_session())


def test_get_smartapi_tokens_by_any_and_all_condition(session):
    """
    Test the get_smartapi_tokens_by_any_condition
    """

    db_file_path = Path(SQLITE_DB_URL.split("sqlite:///")[-1])
    remove_at_end = not db_file_path.exists()

    try:
        create_smartapi_tokens_db(True)

        # Insert test data
        token1 = SmartAPIToken(
            name="INFY",
            symbol="INFY-EQ",
            expiry="",
            strike=-1.0,
            instrument_type="",
            tick_size=5.0,
            token="1594",
            lot_size=1,
            exch_seg="NSE",
        )

        result = get_smartapi_tokens_by_any_condition(session, symbol="INFY-EQ")
        assert token1.to_dict() == result[0].to_dict()

        result = get_smartapi_tokens_by_any_condition(session, symbol="SBI-EQ")
        assert not result

        result = get_smartapi_tokens_by_all_conditions(session, symbol="INFY-EQ")
        assert token1.to_dict() == result[0].to_dict()

        result = get_smartapi_tokens_by_all_conditions(session, symbol="SBI-EQ")
        assert not result

    finally:
        if remove_at_end:
            db_file_path.unlink()
