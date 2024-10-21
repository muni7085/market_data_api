import json
from pathlib import Path

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from app.data_layer.data_saver import DataSaver
from app.utils.common.logger import get_logger
import csv
from datetime import datetime

logger = get_logger(Path(__file__).name)


@DataSaver.register("csv_saver")
class CSVDataSaver(DataSaver):
    def __init__(self, consumer: KafkaConsumer, csv_file_path: str | Path) -> None:
        self.consumer = consumer

        if isinstance(csv_file_path, str):
            csv_file_path = Path(csv_file_path)

        file_name = csv_file_path.stem + f"_{datetime.now().strftime('%Y_%m_%d')}.csv"
        self.csv_file_path = csv_file_path.with_name(file_name)

    def retrieve_and_save(self):
        try:
            idx: int = 0
            print(self.csv_file_path)
            with open(self.csv_file_path, "a",newline="") as file:
                writer = csv.writer(file)
                for idx, message in enumerate(self.consumer):
                    decoded_data = message.value.decode("utf-8")
                    decoded_data = json.loads(decoded_data)
                    if idx == 0:
                        writer.writerow(list(decoded_data.keys()))
                    writer.writerow(list(decoded_data.values()))
                    file.flush()
        except Exception as e:
            logger.error(f"Error while saving data to csv: {e}")
        finally:
            logger.info("%s messages saved to csv", idx)

    @classmethod
    def from_cfg(cls, cfg):
        try:
            return cls(
                KafkaConsumer(
                    cfg.streaming.kafka_topic,
                    bootstrap_servers=cfg.streaming.kafka_server,
                    auto_offset_reset="earliest",
                ),
                cfg.get("csv_file_path"),
            )
        except NoBrokersAvailable:
            logger.error(
                f"No Broker is availble at the address: {cfg.data_source.kafka_server}. No data will be saved."
            )
            return None
