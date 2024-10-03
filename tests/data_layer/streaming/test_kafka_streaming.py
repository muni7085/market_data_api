# pylint: disable=missing-function-docstring
import pytest
from kafka.errors import KafkaError, NoBrokersAvailable

from app.data_layer.streaming.kafka_streaming import KafkaStreaming


####################### FIXTURES #######################
@pytest.fixture
def kafka_server():
    return "localhost:9092"


@pytest.fixture
def kafka_topic():
    return "test-topic"


@pytest.fixture
def kafka_streaming(mocker, kafka_server, kafka_topic):
    # Mock KafkaProducer
    mock_kafka_producer = mocker.MagicMock()
    mocker.patch(
        "app.data_layer.streaming.kafka_streaming.KafkaProducer",
        return_value=mock_kafka_producer,
    )

    return KafkaStreaming(kafka_server, kafka_topic)


####################### TESTS #######################


# Test: 1 (Test the initialization of the KafkaStreaming class)
def test_kafka_streaming_init(mocker, kafka_server, kafka_topic):
    # Mock KafkaProducer
    mock_kafka_producer = mocker.MagicMock()
    mocker.patch(
        "app.data_layer.streaming.kafka_streaming.KafkaProducer",
        return_value=mock_kafka_producer,
    )

    # Initialize KafkaStreaming
    kafka_streaming = KafkaStreaming(kafka_server, kafka_topic)

    assert kafka_streaming.kafka_topic == kafka_topic
    assert kafka_streaming.kafka_producer == mock_kafka_producer


# Test: 2 (Test the initialization of the KafkaStreaming class with failure)
def test_kafka_streaming_init_failure(mocker, kafka_server, kafka_topic):
    # Mock KafkaProducer to raise exception
    mocker.patch(
        "app.data_layer.streaming.kafka_streaming.KafkaProducer",
        side_effect=NoBrokersAvailable("No Brokers Available"),
    )

    # Initialize KafkaStreaming and expect an exception
    with pytest.raises(NoBrokersAvailable):
        KafkaStreaming(kafka_server, kafka_topic)


# Test: 3 (Test the __call__ method of the KafkaStreaming class with successful data sending)
def test_kafka_streaming_call_success(kafka_streaming):
    # Send data to Kafka
    data = "test data"
    kafka_streaming(data)

    # Verify the Kafka producer's send method was called correctly
    kafka_streaming.kafka_producer.send.assert_called_once_with(
        kafka_streaming.kafka_topic, data.encode("utf-8")
    )
    kafka_streaming.kafka_producer.flush.assert_called_once()


# Test: 4 (Test the __call__ method of the KafkaStreaming class with data sending failure)
def test_kafka_streaming_call_failure(mocker, kafka_streaming):
    # Simulate an exception when sending data to Kafka
    kafka_streaming.kafka_producer.send.side_effect = KafkaError("Failed to send")

    # Capture the logger's output
    mock_logger = mocker.patch("app.data_layer.streaming.kafka_streaming.logger")

    # Send data to Kafka and expect an exception
    data = "test data"
    kafka_streaming(data)

    # Verify logger error was called
    mock_logger.error.assert_called_once_with(
        "Error sending data to Kafka: %s", mocker.ANY
    )


# Test: 5 (Test the close method of the KafkaStreaming class with successful closing)
def test_kafka_streaming_close_success(kafka_streaming):
    # Close the Kafka producer
    kafka_streaming.close()

    # Verify close was called
    kafka_streaming.kafka_producer.close.assert_called_once()


# Test: 6 (Test the close method of the KafkaStreaming class with closing failure)
def test_kafka_streaming_close_failure(mocker, kafka_streaming):
    # Simulate an exception when closing Kafka producer
    kafka_streaming.kafka_producer.close.side_effect = KafkaError("Failed to close")

    # Capture the logger's output
    mock_logger = mocker.patch("app.data_layer.streaming.kafka_streaming.logger")

    # Close the Kafka producer and expect an exception
    kafka_streaming.close()

    # Verify logger error was called
    mock_logger.error.assert_called_once_with(
        "Error closing Kafka producer: %s", mocker.ANY
    )


# Test: 7 (Test the from_cfg method of the KafkaStreaming class with successful creation)
def test_kafka_streaming_from_cfg(mocker):
    # Mock KafkaProducer
    mock_kafka_producer = mocker.MagicMock()
    mocker.patch(
        "app.data_layer.streaming.kafka_streaming.KafkaProducer",
        return_value=mock_kafka_producer,
    )

    # Mock config
    cfg = {"kafka_server": "localhost:9092", "kafka_topic": "test-topic"}

    # Create KafkaStreaming from config
    kafka_streaming = KafkaStreaming.from_cfg(cfg)

    # Assertions
    assert kafka_streaming.kafka_topic == "test-topic"
    assert kafka_streaming.kafka_producer == mock_kafka_producer


# Test: 8 (Test the from_cfg method of the KafkaStreaming class with failure)
def test_kafka_streaming_from_cfg_failure(mocker):
    # Mock KafkaProducer to raise exception
    mocker.patch(
        "app.data_layer.streaming.kafka_streaming.KafkaProducer",
        side_effect=KafkaError("Failed to connect"),
    )

    # Capture the logger's output
    mock_logger = mocker.patch("app.data_layer.streaming.kafka_streaming.logger")

    # Mock config
    cfg = {"kafka_server": "localhost:9092", "kafka_topic": "test-topic"}

    # Create KafkaStreaming from config
    kafka_streaming = KafkaStreaming.from_cfg(cfg)

    # Verify that None is returned and the error was logged
    assert kafka_streaming is None
    mock_logger.error.assert_called_once_with(
        "Error creating KafkaStreaming object: %s", mocker.ANY
    )
