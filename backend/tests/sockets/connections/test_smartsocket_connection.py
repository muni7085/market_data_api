"""
This module contains the tests for the SmartSocketConnection class.
"""

# pylint: disable=missing-function-docstring, redefined-outer-name
from copy import deepcopy
from typing import Any, cast

import pytest
from app.data_layer.database.models.smartapi_model import SmartAPIToken
from app.sockets.connections import SmartSocketConnection
from app.utils.common.exceptions import SymbolNotFoundException
from app.utils.common.types.financial_types import Exchange
from omegaconf import OmegaConf
from pytest_mock import MockerFixture, MockType


#################### Fixtures ####################
@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MockType:
    return mocker.patch("app.sockets.connections.smartsocket_connection.logger")


@pytest.fixture
def mock_smartsocket(mocker: MockerFixture) -> MockType:
    smartsocket = mocker.patch(
        "app.sockets.connections.smartsocket_connection.SmartSocket",
    )
    smartsocket.initialize_socket.return_value = smartsocket

    return smartsocket


@pytest.fixture
def mock_get_smartapi_tokens_by_all_conditions(mocker: MockerFixture) -> MockType:
    return mocker.patch(
        "app.sockets.connections.smartsocket_connection.get_smartapi_tokens_by_all_conditions",
    )


@pytest.fixture
def mock_validate_symbol_and_get_token(mocker: MockerFixture) -> MockType:
    return mocker.patch(
        "app.sockets.connections.smartsocket_connection.validate_symbol_and_get_token",
    )


@pytest.fixture
def mock_streamer(mocker: MockerFixture) -> MockType:
    return mocker.patch("app.sockets.connections.smartsocket_connection.Streamer")


@pytest.fixture
def mock_init_from_cfg(mocker: MockerFixture, mock_streamer) -> MockType:
    return mocker.patch(
        "app.sockets.connections.smartsocket_connection.init_from_cfg",
        return_value=mock_streamer,
    )


@pytest.fixture
def smartapi_tokens() -> tuple[list[SmartAPIToken], dict[str, str]]:
    return (
        [
            SmartAPIToken(
                token="256265",
                symbol="INFY",
                exchange="NSE",
                instrument_type="EQ",
                name="Infosys Limited",
            ),
            SmartAPIToken(
                token="256267",
                symbol="TCS",
                exchange="NSE",
                instrument_type="EQ",
                name="Tata Consultancy Services Limited",
            ),
        ],
        {"256265": "INFY", "256267": "TCS"},
    )


@pytest.fixture
def connection_cfg() -> dict:
    return {
        "name": "smartsocket_connection",
        "provider": {
            "name": "smartsocket",
            "correlation_id": "smart00001",
            "subscription_mode": "snap_quote",
            "debug": False,
        },
        "streaming": {
            "name": "kafka",
            "kafka_topic": "smartsocket",
            "kafka_server": "localhost:9092",
        },
        "symbols": None,
        "exchange_type": "nse_cm",
        "num_connections": 1,
        "current_connection_number": 0,
        "use_thread": True,
        "num_tokens_per_instance": 10,
    }


@pytest.fixture
def connection(
    connection_cfg: dict,
    smartapi_tokens: tuple[list[SmartAPIToken], dict[str, str]],
    mock_get_smartapi_tokens_by_all_conditions: MockType,
) -> SmartSocketConnection:
    cfg = OmegaConf.create(connection_cfg)
    mock_get_smartapi_tokens_by_all_conditions.return_value = smartapi_tokens[0]

    return cast(SmartSocketConnection, SmartSocketConnection.from_cfg(cfg))


def validate_invalid_connection(
    connection: Any,
    mock_logger: MockType,
    mock_smartsocket: MockType,
    mock_init_from_cfg: MockType,
):
    """
    This function validates the connection object when the configuration is invalid.
    """

    assert connection is None
    mock_logger.error.assert_called_with(
        "Instance %d has no tokens to subscribe to, exiting...", 0
    )

    mock_smartsocket.initialize_socket.assert_called_once()
    mock_init_from_cfg.assert_called_once()
    mock_smartsocket.set_tokens.assert_not_called()

    # Reset mock calls for the next test
    mock_smartsocket.reset_mock()
    mock_init_from_cfg.reset_mock()
    mock_logger.reset_mock()


#################### Tests ####################


# Test: 1
def test_init_from_cfg_valid_cfg(
    connection_cfg: dict,
    mock_smartsocket: MockType,
    mock_init_from_cfg: MockType,
    mock_streamer: MockType,
    smartapi_tokens: tuple[list[SmartAPIToken], dict[str, str]],
    mock_get_smartapi_tokens_by_all_conditions: MockType,
):
    """
    Test the initialization of the SmartSocketConnection object from a valid configuration.
    """

    mock_get_smartapi_tokens_by_all_conditions.return_value = smartapi_tokens[0]
    cfg = OmegaConf.create(connection_cfg)
    connection = SmartSocketConnection.from_cfg(cfg)

    assert connection is not None
    assert connection.websocket == mock_smartsocket

    mock_init_from_cfg.assert_called_with(cfg.streaming, mock_streamer)
    assert mock_init_from_cfg.return_value == mock_streamer

    mock_smartsocket.set_tokens.assert_called_once()
    mock_smartsocket.initialize_socket.assert_called_once()


# Test: 2
def test_init_from_cfg_invalid_cfg(
    connection_cfg: dict,
    mock_logger: MockType,
    mock_smartsocket: MockType,
    mock_init_from_cfg: MockType,
    mock_get_smartapi_tokens_by_all_conditions: MockType,
):
    """
    Test the initialization of the SmartSocketConnection object from all the invalid
    configurations.
    """

    # Test: 2.2 ( Invalid exchange type )
    connection_cfg_cp = deepcopy(connection_cfg)

    connection_cfg["exchange_type"] = "invalid_exchange_type"
    cfg = OmegaConf.create(connection_cfg)
    connection = SmartSocketConnection.from_cfg(cfg)
    mock_logger.error.assert_called_with(
        "Instance %d has no tokens to subscribe to, exiting...", 0
    )
    validate_invalid_connection(
        connection, mock_logger, mock_smartsocket, mock_init_from_cfg
    )

    # Test: 2.3 ( Number of tokens per instance is 0, meaning no tokens to subscribe to )
    connection_cfg = deepcopy(connection_cfg_cp)
    connection_cfg["num_tokens_per_instance"] = 0
    cfg = OmegaConf.create(connection_cfg)
    mock_get_smartapi_tokens_by_all_conditions.return_value = []
    connection = SmartSocketConnection.from_cfg(cfg)

    validate_invalid_connection(
        connection, mock_logger, mock_smartsocket, mock_init_from_cfg
    )

    # Test: 2.4 ( Invalid symbols )
    connection_cfg = deepcopy(connection_cfg_cp)
    connection_cfg["symbols"] = ["FAKE_SYMBOL"]
    cfg = OmegaConf.create(connection_cfg)
    connection = SmartSocketConnection.from_cfg(cfg)

    validate_invalid_connection(
        connection, mock_logger, mock_smartsocket, mock_init_from_cfg
    )


# Test: 3
def test_get_equity_stock_tokens(
    connection: SmartSocketConnection,
    mock_get_smartapi_tokens_by_all_conditions: MockType,
    smartapi_tokens: MockType,
):
    """
    Test the get_equity_stock_tokens method of the SmartSocketConnection class
    with valid and invalid exchange types.
    """
    mock_get_smartapi_tokens_by_all_conditions.return_value = smartapi_tokens[0]
    stocks = connection.get_equity_stock_tokens(Exchange.NSE, "EQ")

    assert stocks == smartapi_tokens[1]


# Test: 4
def test_get_tokens_from_symbols(
    mocker: MockType,
    connection: SmartSocketConnection,
    smartapi_tokens: tuple[list[SmartAPIToken], dict[str, str]],
    mock_logger: MockType,
):
    """
    Test the get_tokens_from_symbols method of the SmartSocketConnection class
    with valid and invalid symbols.
    """
    # Test: 4.1 ( Test with valid symbols and exchange type )
    token_symbol = list(smartapi_tokens[1].items())[0]
    mocker.patch(
        "app.sockets.connections.smartsocket_connection.validate_symbol_and_get_token",
        return_value=token_symbol,
    )

    stocks = connection.get_tokens_from_symbols([token_symbol[0]], Exchange.NSE)

    assert stocks == {token_symbol[0]: token_symbol[1]}

    # Test: 4.2 ( Test with invalid symbols )
    mocker.patch(
        "app.sockets.connections.smartsocket_connection.validate_symbol_and_get_token",
        side_effect=SymbolNotFoundException("FAKE_SYMBOL"),
    )
    stocks = connection.get_tokens_from_symbols(["FAKE_SYMBOL"], Exchange.NSE)

    assert stocks == {}
    mock_logger.error.assert_called_once_with(
        "Invalid symbols: %s discarded for subscription", ["FAKE_SYMBOL"]
    )


# Test: 5
def test_get_tokens(
    connection: SmartSocketConnection,
    mock_logger: MockType,
    mock_validate_symbol_and_get_token: MockType,
    mock_get_smartapi_tokens_by_all_conditions: MockType,
    smartapi_tokens: tuple[list[SmartAPIToken], dict[str, str]],
):
    """
    Test the get_tokens method of the SmartSocketConnection class with all
    the possible scenarios.
    """
    # Test: 5.1 ( Test with exchange type as None and symbols as None )
    tokens = connection.get_tokens(exchange_segment=None, symbols=None)  # type: ignore
    mock_logger.error.assert_called_once_with(
        "Exchange type not provided in the configuration, exiting..."
    )
    mock_logger.reset_mock()
    assert tokens == {}

    # Test: 5.2 ( Test with invalid exchange type )
    tokens = connection.get_tokens(exchange_segment="nse_fo", symbols=["INFY"])
    mock_logger.error.assert_called_once_with(
        "Invalid exchange type provided in the configuration: %s", "nse_fo"
    )
    assert tokens == {}
    mock_logger.reset_mock()

    # Test: 5.3 ( Test with invalid exchange type )
    tokens = connection.get_tokens(exchange_segment="nse_fo")
    mock_logger.error.assert_called_once_with(
        "Invalid exchange type provided in the configuration: %s", "nse_fo"
    )
    assert tokens == {}

    # Test: 5.4 ( Test with exchange type as None and symbols )
    mock_validate_symbol_and_get_token.return_value = ("256265", "INFY")
    tokens = connection.get_tokens(exchange_segment=None, symbols=["INFY"])  # type: ignore
    mock_logger.info.assert_called_once_with(
        "Exchange type not provided in the configuration, considering the NSE exchange type"
    )
    mock_validate_symbol_and_get_token.assert_called_once_with(Exchange.NSE, "INFY")
    assert tokens == {"256265": "INFY"}
    mock_logger.reset_mock()
    mock_validate_symbol_and_get_token.reset_mock()

    # Test: 5.5 ( Test with NSE exchange  and symbols )
    tokens = connection.get_tokens(exchange_segment="nse_cm", symbols=["INFY"])
    mock_validate_symbol_and_get_token.assert_called_once_with(Exchange.NSE, "INFY")
    assert tokens == {"256265": "INFY"}
    mock_validate_symbol_and_get_token.reset_mock()

    # Test: 5.6 ( Test with BSE exchange and symbols )
    tokens = connection.get_tokens(exchange_segment="bse_cm", symbols=["INFY"])
    mock_validate_symbol_and_get_token.assert_called_once_with(Exchange.BSE, "INFY")
    assert tokens == {"256265": "INFY"}

    # Test: 5.7 ( Test with NSE exchange only )
    mock_get_smartapi_tokens_by_all_conditions.return_value = smartapi_tokens[0]
    tokens = connection.get_tokens(exchange_segment="nse_cm")

    mock_get_smartapi_tokens_by_all_conditions.assert_any_call(
        exchange="NSE", instrument_type="EQ"
    )
    assert tokens == {
        smartapi_token.token: smartapi_token.symbol
        for smartapi_token in smartapi_tokens[0]
    }

    # Test: 5.8 ( Test with BSE exchange only )
    tokens = connection.get_tokens(exchange_segment="bse_cm")

    mock_get_smartapi_tokens_by_all_conditions.assert_any_call(
        exchange="BSE", instrument_type="EQ"
    )
    assert tokens == {
        smartapi_token.token: smartapi_token.symbol
        for smartapi_token in smartapi_tokens[0]
    }
