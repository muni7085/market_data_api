import time
from typing import Any

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.routers.smartapi.historical_equity_data.historical_equity_data import router
from app.schemas.stock_model import HistoricalStockPriceInfo

client = TestClient(router)


def validate_exception(endpoint_url: str, expected_error: dict[str, Any]):
    """
    Test function to validate exception.

    This function checks if the expected exception is valid or not
    for the request with given endpoint_url.

    Parameters:
    -----------
    endpoint_url: `str`
        URL to request data from historical_stock_data endpoint.
    expected_error: `dict[str, Any]`
        Expected exception for the request with given endpoint_url.
    """
    try:
        # Make a GET request to the endpoint URL
        client.get(endpoint_url)
    except HTTPException as http_exc:
        # Check if the status code of the exception matches the expected error status code
        assert http_exc.status_code == expected_error["status_code"]
        # Check if the detail message of the exception matches the expected error detail
        assert http_exc.detail == expected_error["error"]


def validate_input_stock_data(input_stock_data: dict[str, Any]):
    """Verifies whether the given input stock data is valid or raises an exception.

    Parameters:
    -----------
    input_stock_data: `dict`
        Details of the stock to be validated.
    """
    endpoint_url = (
        f"/smart-api/equity/history/{input_stock_data['input_stock_symbol']}?interval={input_stock_data['input_interval']}"
        f"&start_date={input_stock_data['input_from_date']}&end_date={input_stock_data['input_to_date']}"
    )

    if input_stock_data["status_code"] == 200:
        # Send a GET request to the endpoint URL
        response = client.get(endpoint_url)

        # Assert that the response status code matches the expected status code
        assert response.status_code == input_stock_data["status_code"]
        data = response.json()
        # Assert that the response contains JSON data
        assert response.json() is not None

        # Assert that the response is list of stock data
        assert isinstance(data, list)

        # Parse the response JSON into a HistoricalStockPriceInfo object
        smart_api_stock_price_info = HistoricalStockPriceInfo.parse_obj(data[0])

        # # Assert that the stock_price_info object is an instance of StockPriceInfo
        assert isinstance(smart_api_stock_price_info, HistoricalStockPriceInfo)

    else:
        validate_exception(endpoint_url, input_stock_data)
    time.sleep(1)


def test_historical_stock_data_with_different_stock_symbols(
    stock_symbol_io: list[dict[str, Any]]
):
    """Tests the historical stock data endpoint with various possible stock symbols
    that are either valid or invalid.

    Parameters:
    -----------
    stock_symbol_io: `list[dict[str, Any]]`
        Input stock data with different stock symbols.
    """

    for stock_symbol_data in stock_symbol_io:
        validate_input_stock_data(stock_symbol_data)


def test_historical_stock_data_with_different_intervals(
    candlestick_interval_io: list[dict[str, Any]]
):
    """Tests the historical stock data endpoint with various possible candlestick intervals
    that are either valid or invalid.

    Parameters:
    -----------
    candlestick_interval_io: `list[dict[str, Any]]`
        Input stock data with different candlestick intervals.
    """
    for interval_data in candlestick_interval_io:
        validate_input_stock_data(interval_data)


def test_historical_stock_data_with_datetime_formats(
    different_datetime_formats_io: list[dict[str, Any]]
):
    """Tests the historical stock data endpoint with various possible datetime formats
    that are either valid or invalid.

    Parameters:
    -----------
    different_datetime_formats_io: `list[dict[str, Any]]`
        Input stock data with different datetime formats.
    """
    for datetime_format_data in different_datetime_formats_io:
        validate_input_stock_data(datetime_format_data)


def test_historical_stock_data_on_holidays(holiday_dates_io: list[dict[str, Any]]):
    """Tests the historical stock data endpoint on market holidays.

    Parameters:
    -----------
    holiday_dates_io: `list[dict[str, Any]]`
        Input stock data on market holidays.
    """
    for holiday_date_data in holiday_dates_io:
        validate_input_stock_data(holiday_date_data)


def test_historical_stock_data_on_data_unavailable_dates(
    data_unavailable_dates_io: list[dict[str, Any]]
):
    """Tests the historical stock data endpoint on data unavailable time periods or dates.

    Parameters:
    -----------
    data_unavailable_dates_io: `list[dict[str, Any]]`
        Input stock data on data unavailable time periods.
    """
    for data_unavailable_date_data in data_unavailable_dates_io:
        validate_input_stock_data(data_unavailable_date_data)


def test_historical_stock_data_invalid_trading_time(
    invalid_trading_time_io: dict[str, Any]
):
    """Tests the historical stock data endpoint with invalid trading time.

    Parameters:
    -----------
    invalid_trading_time_io: `dict[str, Any]`
        Input stock data with invalid trading time.
    """
    validate_input_stock_data(invalid_trading_time_io)


def test_historical_stock_data_invalid_date_range(date_range_io: dict[str, Any]):
    """Tests the historical stock data endpoint with invalid date range where date range can exceeds
    maximum or minimum limit per request.

    Parameters:
    -----------
    date_range_io: `dict[str, Any]`
        Input stock data with invalid date range.
    """
    validate_input_stock_data(date_range_io)
