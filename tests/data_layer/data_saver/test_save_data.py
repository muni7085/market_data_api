import pytest
from omegaconf import DictConfig, OmegaConf
from tempfile import TemporaryDirectory
from app.data_layer.data_saver import DataSaver, CSVDataSaver, JSONLDataSaver
from app.data_layer.data_saver.save_data import main, init_from_cfg
from pytest_mock import MockerFixture, MockType


@pytest.fixture
def csv_config() -> DictConfig:
    """
    Configuration for the CSVDataSaver.

    Returns:
    --------
    ``DictConfig``
        Configuration for the CSVDataSaver
    """
    return OmegaConf.create(
        {
            "name": "csv_saver",
            "csv_file_path": TemporaryDirectory().name + "/test.csv",
            "streaming": {
                "kafka_topic": "test_topic",
                "kafka_server": "localhost:9092",
            },
        }
    )


@pytest.fixture
def mock_csv_consumer(mocker: MockerFixture) -> MockType:
    """
    Mock the KafkaConsumer object.
    """
    return mocker.patch("app.data_layer.data_saver.csv_saver.KafkaConsumer")


@pytest.fixture
def csv_saver(
    mock_csv_consumer: MockType, csv_config: DictConfig, mocker: MockerFixture
) -> CSVDataSaver:
    """
    Fixture to return the CSVDataSaver object.
    """
    mock_csv_consumer.return_value = mocker.MagicMock()

    return CSVDataSaver.from_cfg(csv_config)


@pytest.fixture
def jsonl_config() -> DictConfig:
    """
    Configuration for the JSONLDataSaver.

    Returns:
    --------
    ``DictConfig``
        Configuration for the JSONLDataSaver
    """
    return OmegaConf.create(
        {
            "name": "jsonl_saver",
            "jsonl_file_path": TemporaryDirectory().name + "/test.jsonl",
            "streaming": {
                "kafka_topic": "test_topic",
                "kafka_server": "localhost:9092",
            },
        }
    )


@pytest.fixture
def mock_json_consumer(mocker: MockerFixture) -> MockType:
    """
    Mock the KafkaConsumer object.
    """
    return mocker.patch("app.data_layer.data_saver.jsonl_saver.KafkaConsumer")


@pytest.fixture
def jsonl_saver(
    mock_json_consumer: MockType, jsonl_config: DictConfig, mocker: MockerFixture
) -> JSONLDataSaver:
    """
    Fixture to return the JSONLDataSaver object.
    """
    mock_json_consumer.return_value = mocker.MagicMock()

    return JSONLDataSaver.from_cfg(jsonl_config)

@pytest.fixture
def mock_init_from_cfg(mocker, jsonl_saver, csv_saver) -> DataSaver:
    return mocker.patch(
        "app.data_layer.data_saver.save_data.init_from_cfg"
    )


@pytest.fixture
def data_saver_config():
    """
    Configuration for the DataSaver.

    Returns:
    --------
    ``DictConfig``
        Configuration for the DataSaver
    """
    return OmegaConf.create(
        {
            "data_saver": [
                {
                    "csv_saver": "csv_saver_config",
                    "jsonl_saver": "jsonl_saver_config",
                }
            ]
        }
    )

def test_main_data_saver(
    mocker: MockerFixture,
    csv_saver: CSVDataSaver,
    jsonl_saver: JSONLDataSaver,
    data_saver_config: DictConfig,
    mock_init_from_cfg
):
    """
    Test the main function for the data saver.
    """
    mock_init_from_cfg.side_effect = [csv_saver, jsonl_saver]
    mock_thread = mocker.patch("app.data_layer.data_saver.save_data.Thread")
    mock_thread.return_value = mocker.MagicMock()
    mock_thread.start = mocker.MagicMock()
    mock_thread.join = mocker.MagicMock()

    main(data_saver_config)
    mock_thread.assert_called_once_with(target=csv_saver.retrieve_and_save)
    
    print(mock_thread.method_calls)
    print(mock_thread.mock_calls)
    mock_thread().start.assert_called_once()
    mock_thread().join.assert_called_once()
    assert False