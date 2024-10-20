import json
from pathlib import Path

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from app.sockets.websocket_datahandler.data_saver import DataSaver
from app.utils.common.logger import get_logger
import csv

logger = get_logger(Path(__file__).name)


@DataSaver.register("sqlite_saver")
class SqliteDataSaver(DataSaver):
    def __init__(self, consumer: KafkaConsumer, csv_file_path: str | Path) -> None:
        self.consumer = consumer
        self.csv_file_path = csv_file_path

    def retrieve_and_save(self):
        try:
            idx: int = 0
            with open(self.csv_file_path, "w") as file:
                writer = csv.writer(file)
                for idx, message in enumerate(self.consumer):
                    decoded_data = message.value.decode("utf-8")
                    decoded_data = json.loads(decoded_data)
                    if idx == 0:
                        writer.writerow(message.value.keys())
                    writer.writerow(decoded_data.values())
        except Exception as e:
            logger.error(f"Error while saving data to csv: {e}")
        finally:
            logger.info("%s messages saved to csv", idx)

    @classmethod
    def from_cfg(cls, cfg):
        try:
            return cls(
                KafkaConsumer(
                    cfg.data_source.kafka_topic,
                    bootstrap_servers=cfg.data_source.kafka_server,
                    auto_offset_reset="earliest",
                ),
                cfg.data_source.csv_file_path,
            )
        except NoBrokersAvailable:
            logger.error(
                f"No Broker is availble at the address: {cfg.data_source.kafka_server}. No data will be saved."
            )
            return None
