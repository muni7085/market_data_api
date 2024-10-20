import json
from pathlib import Path

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from app.data_layer.database.sqlite.crud.websocket_crud import insert_data
from app.data_layer.database.sqlite.models.websocket_models import SocketStockPriceInfo
from app.data_layer.data_saver import DataSaver
from app.utils.common.logger import get_logger
from app.utils.smartapi.smartsocket_types import ExchangeType
from app.data_layer.database.sqlite.sqlite_db_connection import (
    create_db_and_tables,
    create_sqlite_engine,
    get_session,
)
from datetime import datetime

logger = get_logger(Path(__file__).name)


@DataSaver.register("sqlite_saver")
class SqliteDataSaver(DataSaver):
    def __init__(self, consumer: KafkaConsumer, sqlite_db: str) -> None:
        self.consumer = consumer

        current_date = datetime.now().strftime("%Y_%m_%d")
        self.sqlite_db = f"sqlite:///{sqlite_db}/{current_date}.sqlite3"
        self.engine = create_sqlite_engine(self.sqlite_db)
        create_db_and_tables(self.engine)

    def save_stock_data(self, data):
        socket_stock_price_info = SocketStockPriceInfo(
            last_traded_timestamp=data["last_traded_timestamp"],
            token=data["token"],
            retrieval_timestamp=data["retrieval_timestamp"],
            socket_name=data["socket_name"],
            exchange_timestamp=data["exchange_timestamp"],
            name=data["name"],
            last_traded_price=data["last_traded_price"],
            last_traded_quantity=data.get("last_traded_quantity"),
            average_traded_price=data.get("average_traded_price"),
            volume_trade_for_the_day=data.get("volume_trade_for_the_day"),
            total_buy_quantity=data.get("total_buy_quantity"),
            total_sell_quantity=data.get("total_sell_quantity"),
        )
        insert_data(socket_stock_price_info, session=get_session(self.engine))

    def save(self, data):
        decoded_data = data.decode("utf-8")
        decoded_data = json.loads(decoded_data)

        if decoded_data["exchange_type"] == ExchangeType.NSE_CM.name:
            self.save_stock_data(decoded_data)
        else:
            logger.error(
                f"Security type {decoded_data['security_type']} is not supported"
            )

    def retrieve_and_save(self):
        for message in self.consumer:
            self.save(message.value)

    @classmethod
    def from_cfg(cls, cfg):
        try:
            return cls(
                # KafkaConsumer(
                #     cfg.data_source.kafka_topic,
                #     bootstrap_servers=cfg.data_source.kafka_server,
                #     auto_offset_reset="earliest",
                # ),
                None,
                cfg.get("sqlite_db"),
            )
        except NoBrokersAvailable:
            logger.error(
                f"No Broker is availble at the address: {cfg.data_source.kafka_server}. No data will be saved."
            )
            return None
