from pathlib import Path

from kafka import KafkaProducer

from app.sockets.websocket_datahandler.on_data_callbacks.base_callback import (
    BaseCallback,
)
from app.utils.common.logger_utils import get_logger

logger = get_logger(Path(__file__).name)


@BaseCallback.register("kafka")
class KafkaCallback(BaseCallback):
    def __init__(self, kafka_server, kafka_topic):
        self.kafka_producer = None
        self.kafka_topic = kafka_topic
        try:
            self.kafka_producer = KafkaProducer(bootstrap_servers=kafka_server)
        except Exception as e:
            logger.error(f"Error in KafkaCallback initialization: {e}")

    def __call__(self, data):
        if self.kafka_producer is None:
            logger.error(
                "Kafka producer is not initialized. Not sending data to Kafka."
            )
            return
        try:
            data = data.encode("utf-8")
            self.kafka_producer.send(self.kafka_topic, data)
            self.kafka_producer.flush()
        except Exception as e:
            logger.error(f"Error sending data to Kafka: {e}")

    def close(self):
        if self.kafka_producer:
            try:
                self.kafka_producer.close()
            except Exception as e:
                logger.error(f"Error closing Kafka producer: {e}")

    @classmethod
    def from_cfg(cls, cfg):
        return cls(cfg["kafka_server"], cfg["kafka_topic"])
