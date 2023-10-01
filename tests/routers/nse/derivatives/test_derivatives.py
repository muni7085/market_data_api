from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.routers.nse.derivatives.derivatives import router

client = TestClient(router)


def get_next_thursday():
    today = datetime.today()
    days_ahead = 3 - today.weekday()
    if days_ahead < 0:
        days_ahead += 7
    next_thursday = today + timedelta(days=days_ahead)

    return next_thursday.strftime("%d-%b-%Y")


def test_index_option_chain():
    expiry_data = get_next_thursday()
    response = client.get(
        f"/nse/derivatives/NIFTY?expiry_date={expiry_data}&derivative_type=index"
    )
    assert response.status_code == 200
