import json
from collections import namedtuple
from datetime import datetime
from tempfile import TemporaryDirectory

import pytest
from kafka.errors import NoBrokersAvailable
from omegaconf import DictConfig, OmegaConf

from app.data_layer.data_saver import DataSaver, SqliteDataSaver
from app.data_layer.database.sqlite.crud.websocket_crud import get_all_stock_price_info
from app.data_layer.database.sqlite.models.websocket_models import SocketStockPriceInfo
from app.data_layer.database.sqlite.sqlite_db_connection import get_session
from app.utils.common import init_from_cfg

Message = namedtuple("Message", ["value"])


####################################### FIXTURES #######################################
@pytest.fixture
def kafka_data():
    return [
        {
            "subscription_mode": 3,
            "exchange_type": 1,
            "token": "10893",
            "sequence_number": 18537152,
            "exchange_timestamp": 1729506514000,
            "last_traded_price": 13468,
            "subscription_mode_val": "SNAP_QUOTE",
            "last_traded_quantity": 414,
            "average_traded_price": 13529,
            "volume_trade_for_the_day": 131137,
            "total_buy_quantity": 0.0,
            "total_sell_quantity": 0.0,
            "open_price_of_the_day": 13820,
            "high_price_of_the_day": 13820,
            "low_price_of_the_day": 13365,
            "closed_price": 13726,
            "last_traded_timestamp": 1729504796,
            "open_interest": 0,
            "open_interest_change_percentage": 0,
            "name": "DBOL",
            "socket_name": "smartapi",
            "retrieval_timestamp": "1729532024.309936",
            "exchange": "NSE_CM",
        },
        {
            "subscription_mode": 3,
            "exchange_type": 1,
            "token": "13658",
            "sequence_number": 18578253,
            "exchange_timestamp": 1729506939000,
            "last_traded_price": 40260,
            "subscription_mode_val": "SNAP_QUOTE",
            "last_traded_quantity": 50,
            "average_traded_price": 40510,
            "volume_trade_for_the_day": 13846,
            "total_buy_quantity": 0.0,
            "total_sell_quantity": 0.0,
            "open_price_of_the_day": 41220,
            "high_price_of_the_day": 41270,
            "low_price_of_the_day": 39685,
            "closed_price": 41000,
            "last_traded_timestamp": 1729505946,
            "open_interest": 0,
            "open_interest_change_percentage": 0,
            "name": "GEECEE",
            "socket_name": "smartapi",
            "retrieval_timestamp": "1729532024.31136",
            "exchange": 1,
        },
    ]


@pytest.fixture
def mock_consumer(mocker):
    return mocker.patch("app.data_layer.data_saver.sqlite_saver.KafkaConsumer")


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("app.data_layer.data_saver.sqlite_saver.logger")


@pytest.fixture
def sqlite_config() -> DictConfig:
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
def sqlite_saver(mock_consumer, sqlite_config, mocker, kafka_data):
    mock_consumer.return_value = mocker.MagicMock()
    return SqliteDataSaver.from_cfg(sqlite_config)


####################################### TESTS #######################################


def validate_init(sqlite_saver, mock_consumer, sqlite_config):
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


def test_init(mock_consumer, mocker, sqlite_config, mock_logger):
    mock_consumer.return_value = mocker.MagicMock()

    sqlite_saver = SqliteDataSaver.from_cfg(sqlite_config)
    validate_init(sqlite_saver, mock_consumer, sqlite_config)
    mock_consumer.reset_mock()

    sqlite_saver = init_from_cfg(sqlite_config, DataSaver)
    validate_init(sqlite_saver, mock_consumer, sqlite_config)
    mock_consumer.reset_mock()

    consumer = mock_consumer(
        sqlite_config.streaming.kafka_topic,
        bootstrap_servers=sqlite_config.streaming.kafka_server,
        auto_offset_reset="earliest",
    )
    sqlite_saver = SqliteDataSaver(consumer, sqlite_config.sqlite_db)
    validate_init(sqlite_saver, mock_consumer, sqlite_config)
    mock_consumer.reset_mock()

    mock_consumer.side_effect = NoBrokersAvailable()
    sqlite_saver = SqliteDataSaver.from_cfg(sqlite_config)
    assert sqlite_saver is None
    mock_logger.error.assert_called_once_with(
        f"No Broker is availble at the address: {sqlite_config.streaming.kafka_server}. No data will be saved."
    )
    mock_consumer.assert_called_once_with(
        sqlite_config.streaming.kafka_topic,
        bootstrap_servers=sqlite_config.streaming.kafka_server,
        auto_offset_reset="earliest",
    )


def test_retrieve_and_save(sqlite_saver, mock_logger, kafka_data):
    encoded_data = [
        Message(value=json.dumps(data).encode("utf-8")) for data in kafka_data
    ]
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

    kafka_data[0]["exchange"] = -1
    encoded_data = [
        Message(value=json.dumps(data).encode("utf-8")) for data in kafka_data
    ]

    sqlite_saver.consumer.__iter__.return_value = encoded_data
    sqlite_saver.retrieve_and_save()
    mock_logger.error.assert_called_once_with("Exchange type -1 is not supported")
