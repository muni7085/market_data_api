import pytest
from app.utils.date_utils import get_date


@pytest.fixture
def get_option_chain_io():
    return [
        {
            "input": [get_date("thursday"), "NIFTY", "index"],
            "output": None,
        },
        {
            "input": [get_date("thursday", True), "TCS", "stock"],
            "output": None,
        },
        {
            "input": [get_date("tuesday", True), "INFY", "stock"],
            "output": {
                "status_code": 400,
                "detail": {
                    "Error": f"No expiry for {'INFY'} on {get_date('tuesday',True)}"
                },
            },
        },
    ]
