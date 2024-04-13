# pylint: disable=missing-function-docstring
from typing import Any

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.routers.smartapi.smartapi.smartapi import router
from app.schemas.stock_model import SmartAPIStockPriceInfo

client = TestClient(router)


def validate_exception(endpoint_url: str, expected_error: dict[str, Any]):
    """
    Test function to validate exception.

    This function checks if the exception is valid or not
    for the given invalid input request.

    Parameters:
    -----------
    endpoint_url: `str`
        url
    expected_error: `dict[str, Any]`
        _description_
    """

    try:
        # Make a GET request to the endpoint URL
        client.get(endpoint_url)
    except HTTPException as http_exc:
        # Check if the status code of the exception matches the expected error status code
        assert http_exc.status_code == expected_error["status_code"]
        # Check if the detail message of the exception matches the expected error detail
        assert http_exc.detail == expected_error["error"]


def test_latest_price_quotes(stock_symbol_io: list[dict[str, Any]]):
    """
    Test function to validate latest_price_quote end point.

    This function verifies the operational behaviour of the
    latest_price_quote end point across various input scenarios.

    Parameters:
    -----------
    stock_symbol_io: `list[dict[str, Any]]`
        List of inputs and corresponding outputs.
    """
    for stock_symbol_data in stock_symbol_io:
        endpoint_url = f"/smart-api/equity/price/{stock_symbol_data['input']}"

        if stock_symbol_data["status_code"] == 200:
            # Send a GET request to the endpoint URL
            response = client.get(endpoint_url)

            # Assert that the response status code matches the expected status code
            assert response.status_code == stock_symbol_data["status_code"]

            # Assert that the response contains JSON data
            assert response.json() is not None

            # Parse the response JSON into a SmartAPIStockPriceInfo object
            smart_api_stock_price_info = SmartAPIStockPriceInfo.parse_obj(
                response.json()
            )

            # Assert that the stock_price_info object is an instance of StockPriceInfo
            assert isinstance(smart_api_stock_price_info, SmartAPIStockPriceInfo)

            # Check if the stock token and symbol in the SmartAPIStockPriceInfo object matches the stock symbol data
            assert (
                smart_api_stock_price_info.symbol_token
                == stock_symbol_data["symbol_token"]
            )
            assert smart_api_stock_price_info.symbol == stock_symbol_data["symbol"]

        else:
            validate_exception(endpoint_url, stock_symbol_data)
