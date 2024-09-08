from app.sockets.websocket_datahandler.on_data_callbacks.base_callback import (
    BaseCallback,
)
from kafka import KafkaProducer
from app.utils.common.logger_utils import get_logger
from pathlib import Path

logger = get_logger(Path(__file__).name)

@BaseCallback.register("kafka")
class KafkaCallback(BaseCallback):
    def __init__(self, kafka_server, kafka_topic):
        try:
            self.kafka_producer = KafkaProducer(bootstrap_servers=kafka_server)
            self.kafka_topic = kafka_topic
        except Exception as e:
            logger.error(f"Error in KafkaCallback initialization: {e}")

    def __call__(self, data):
        data=data.encode("utf-8")
        self.kafka_producer.send(self.kafka_topic, data)
        self.kafka_producer.flush()

    @classmethod
    def from_cfg(cls, cfg):
        return cls(cfg["kafka_server"], cfg["kafka_topic"])
