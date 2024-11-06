import json
from collections import namedtuple
from datetime import datetime
from tempfile import TemporaryDirectory
from typing import cast

import pytest
from kafka.errors import NoBrokersAvailable
from omegaconf import DictConfig, OmegaConf
from pytest_mock import MockerFixture, MockType

from app.data_layer.data_saver import DataSaver, SqliteDataSaver
from app.data_layer.database.crud.sqlite.websocket_crud import get_all_stock_price_info
from app.data_layer.database.models.websocket_model import SocketStockPriceInfo
from app.data_layer.database.crud.sqlite_db_connection import get_session
from app.utils.common import init_from_cfg

Message = namedtuple("Message", ["value"])


####################################### FIXTURES #######################################
@pytest.fixture
def mock_consumer(mocker: MockerFixture) -> MockType:
    """
    Mock the KafkaConsumer object.
    """
    return mocker.patch("app.data_layer.data_saver.sqlite_saver.KafkaConsumer")


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MockType:
    """
    Mock the logger object in the SqliteDataSaver.
    """
    return mocker.patch("app.data_layer.data_saver.sqlite_saver.logger")


@pytest.fixture
def sqlite_config() -> DictConfig:
    """
    Configuration for the SqliteDataSaver.
    """
    return OmegaConf.create(
        {
            "name": "sqlite_saver",
            "sqlite_db": TemporaryDirectory().name + "/test.sqlite3",
            "streaming": {
                "kafka_topic": "test_topic",
                "kafka_server": "localhost:9092",
            },
        }
    )


@pytest.fixture
def sqlite_saver(
    mock_consumer: MockType, sqlite_config: MockType, mocker: MockerFixture
) -> SqliteDataSaver:
    """
    Initialize the SqliteDataSaver object.
    """
    mock_consumer.return_value = mocker.MagicMock()

    return cast(SqliteDataSaver, SqliteDataSaver.from_cfg(sqlite_config))


####################################### TESTS #######################################


def validate_init(
    sqlite_saver: SqliteDataSaver | None,
    mock_consumer: MockType,
    sqlite_config: DictConfig,
):
    """
    Validate the initialization of the SqliteDataSaver.
    """
    assert sqlite_saver is not None
    assert sqlite_saver.consumer is not None
    assert sqlite_saver.engine is not None

    current_date = datetime.now().strftime("%Y_%m_%d")
    assert (
        sqlite_saver.sqlite_db
        == f"sqlite:///{sqlite_config.sqlite_db[:-8]}_{current_date}.sqlite3"
    )

    mock_consumer.assert_called_once_with(
        sqlite_config.streaming.kafka_topic,
        bootstrap_servers=sqlite_config.streaming.kafka_server,
        auto_offset_reset="earliest",
    )


# Test: 1
def test_init(
    mock_consumer: MockType,
    mocker: MockerFixture,
    sqlite_config: DictConfig,
    mock_logger: MockType,
):
    """
    Test the initialization of the SqliteDataSaver.
    """
    mock_consumer.return_value = mocker.MagicMock()

    # Test: 1.1 ( Valid initialization from configuration )
    sqlite_saver = SqliteDataSaver.from_cfg(sqlite_config)
    validate_init(sqlite_saver, mock_consumer, sqlite_config)
    mock_consumer.reset_mock()

    # Test: 1.2 ( Valid initialization using init_from_cfg )
    sqlite_saver = cast(SqliteDataSaver, init_from_cfg(sqlite_config, DataSaver))
    validate_init(sqlite_saver, mock_consumer, sqlite_config)
    mock_consumer.reset_mock()

    # Test: 1.3 ( Test constructor initialization )
    consumer = mock_consumer(
        sqlite_config.streaming.kafka_topic,
        bootstrap_servers=sqlite_config.streaming.kafka_server,
        auto_offset_reset="earliest",
    )
    sqlite_saver = SqliteDataSaver(consumer, sqlite_config.sqlite_db)
    validate_init(sqlite_saver, mock_consumer, sqlite_config)
    mock_consumer.reset_mock()

    # Test: 1.4 ( Test NoBrokersAvailable exception )
    mock_consumer.side_effect = NoBrokersAvailable()
    sqlite_saver = SqliteDataSaver.from_cfg(sqlite_config)
    assert sqlite_saver is None
    mock_logger.error.assert_called_once_with(
        "No Broker is availble at the address: %s. No data will be saved.",
        "localhost:9092",
    )
    mock_consumer.assert_called_once_with(
        sqlite_config.streaming.kafka_topic,
        bootstrap_servers=sqlite_config.streaming.kafka_server,
        auto_offset_reset="earliest",
    )


# Test: 2
def test_retrieve_and_save(
    sqlite_saver: SqliteDataSaver, mock_logger: MockType, kafka_data: list[dict]
):
    """
    Test the `retrieve_and_save` method of the SqliteDataSaver.
    """
    encoded_data = [
        Message(value=json.dumps(data).encode("utf-8")) for data in kafka_data
    ]
    # Test: 2.1 ( Test saving data to the sqlite database )
    sqlite_saver.consumer.__iter__.return_value = encoded_data
    sqlite_saver.retrieve_and_save()

    assert sqlite_saver.consumer.__iter__.call_count == 1

    session = get_session(sqlite_saver.engine)
    stock_price_info = get_all_stock_price_info(session)
    inserted_data = [info.to_dict() for info in stock_price_info]
    expected_data = [SocketStockPriceInfo(**data).to_dict() for data in kafka_data]
    for data in expected_data:
        data["exchange"] = "NSE_CM"

    assert inserted_data == expected_data

    # Test: 2.2 ( Test saving data to the sqlite database with invalid exchange type )
    kafka_data[0]["exchange"] = -1
    encoded_data = [
        Message(value=json.dumps(data).encode("utf-8")) for data in kafka_data
    ]

    sqlite_saver.consumer.__iter__.return_value = encoded_data
    sqlite_saver.retrieve_and_save()
    mock_logger.error.assert_called_once_with("Exchange type %s is not supported", -1)
