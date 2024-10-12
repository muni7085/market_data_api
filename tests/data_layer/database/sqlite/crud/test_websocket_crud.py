from typing import Dict
from unittest.mock import MagicMock

import pytest

from app.data_layer.database.sqlite.crud.websocket_crud import (
    insert_data,
    insert_or_ignore,
    upsert,
)
from app.data_layer.database.sqlite.models.websocket_models import SocketStockPriceInfo

#################### FIXTURES ####################


@pytest.fixture
def mock_session(mocker) -> MagicMock:
    """
    Mock the get_session function to return a MagicMock object
    """
    mock_session = mocker.MagicMock()
    mocker.patch(
        "app.data_layer.database.sqlite.crud.websocket_crud.get_session",
        return_value=iter([mock_session]),
    )
    mock_session.__enter__.return_value = mock_session

    return mock_session


@pytest.fixture
def sample_stock_price_info() -> Dict[str, str]:
    """
    Sample stock price info dictionary
    """
    return {
        "token": "256265",
        "retrieval_timestamp": "2021-09-30 10:00:00",
        "last_traded_timestamp": "2021-09-30 09:59:59",
        "socket_name": "smartsocket",
        "exchange_timestamp": "2021-09-30 09:59:59",
        "name": "Infosys Limited",
        "last_traded_price": "1700.0",
        "exchange": "NSE",
        "last_traded_quantity": "100",
        "average_traded_price": "1700.0",
        "volume_trade_for_the_day": "1000",
        "total_buy_quantity": "500",
        "total_sell_quantity": "500",
    }


@pytest.fixture
def sample_socket_stock_price_info() -> SocketStockPriceInfo:
    """
    Sample SocketStockPriceInfo object
    """
    return SocketStockPriceInfo(
        token="256265",
        retrieval_timestamp="2021-09-30 10:00:00",
        last_traded_timestamp="2021-09-30 09:59:59",
        socket_name="smartsocket",
        exchange_timestamp="2021-09-30 09:59:59",
        name="Infosys Limited",
        last_traded_price="1700.0",
        exchange="NSE",
        last_traded_quantity="100",
        average_traded_price="1700.0",
        volume_trade_for_the_day="1000",
        total_buy_quantity="500",
        total_sell_quantity="500",
    )


#################### TESTS ####################


# Test: 1
def test_insert_data_single_dict(
    mock_session: MagicMock, sample_stock_price_info: Dict[str, str]
) -> None:
    """
    Test insert_data with a single dict and `update_existing=False`
    """
    insert_data(sample_stock_price_info, update_existing=False)

    mock_session.exec.assert_called_once()  # Ensure exec was called once
    mock_session.commit.assert_called_once()  # Ensure commit was called


# Test: 2
def test_insert_data_single_dict_upsert(
    mock_session: MagicMock, sample_stock_price_info: Dict[str, str]
) -> None:
    """
    Test insert_data with a single dict and `update_existing=True`
    """
    insert_data(sample_stock_price_info, update_existing=True)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 3
def test_insert_data_empty_input(mock_session: MagicMock, mocker) -> None:
    """
    Test insert_data with empty input (should log a warning and not perform insert)
    """
    mock_logger = mocker.patch(
        "app.data_layer.database.sqlite.crud.websocket_crud.logger"
    )
    insert_data(None, update_existing=False)

    mock_logger.warning.assert_called_once_with(
        "Provided data is empty. Skipping insertion."
    )  # Ensure warning was logged

    mock_session.exec.assert_not_called()  # Ensure exec was not called
    mock_session.commit.assert_not_called()  # Ensure commit was not called


# Test: 4
def test_insert_data_list_dicts(
    mock_session: MagicMock, sample_stock_price_info: Dict[str, str]
) -> None:
    """
    Test insert_data with a list of dicts and `update_existing=False`
    """
    insert_data([sample_stock_price_info], update_existing=False)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 5
def test_insert_data_list_dicts_upsert(
    mock_session: MagicMock, sample_stock_price_info: Dict[str, str]
) -> None:
    """
    Test insert_data with a list of dicts and `update_existing=True`
    """
    insert_data([sample_stock_price_info], update_existing=True)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 6
def test_insert_data_with_object_conversion(
    mock_session: MagicMock, sample_socket_stock_price_info: SocketStockPriceInfo
) -> None:
    """
    Test insert_data with a SocketStockPriceInfo object
    """
    insert_data(sample_socket_stock_price_info, update_existing=False)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 7
def test_upsert(
    mock_session: MagicMock, sample_stock_price_info: Dict[str, str]
) -> None:
    """
    Test upsert logic
    """
    upsert(sample_stock_price_info)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 8
def test_insert_or_ignore(
    mock_session: MagicMock, sample_stock_price_info: Dict[str, str]
) -> None:
    """
    Test insert_or_ignore logic
    """
    insert_or_ignore(sample_stock_price_info)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()
