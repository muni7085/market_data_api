# from pathlib import Path

# import hydra

# from app.database.sqlite.crud.smartapi_curd import get_smartapi_tokens_by_all_conditions
# from app.sockets.tiwsted_sockets.smartsocket import SmartSocket
# from app.utils.common.logger import get_logger
# from functools import partial
# from kafka import KafkaProducer

# logger = get_logger(Path(__file__).name)


# def get_all_stock_tokens(symbol_type: str = None, exch_seg: str = None):

#     smartapi_tokens = get_smartapi_tokens_by_all_conditions(
#         symbol_type=symbol_type, exch_seg=exch_seg
#     )
#     tokens = {token.token:token.symbol for token in smartapi_tokens}

#     return tokens


# def kafka_save_callback(kafka_topic, kafka_producer, data):

#     try:
#         kafka_producer.send(kafka_topic, value=data)
#         return True

#     except Exception as e:
#         logger.error(f"Error while sending data to kafka: {e}")
#         return False


# @hydra.main(config_path="../../configs", config_name="websocket", version_base=None)
# def main(cfg):
#     nse_stock_tokens = get_all_stock_tokens(
#         symbol_type=cfg.exchange_symbol, exch_seg=cfg.exchange
#     )
#     print(nse_stock_tokens)
#     try:
#         kafka_producer = KafkaProducer(
#             bootstrap_servers=cfg.streaming_service.kafka_broker
#         )
#         save_data_callback = partial(
#             kafka_save_callback, cfg.streaming_service.kafka_topic, kafka_producer
#         )
#     except Exception as e:
#         logger.error(f"Error while creating Kafka Producer: {e}")
#         save_data_callback = None

#     smart_socket = SmartSocket.initialize_socket(cfg, save_data_callback)
#     # smart_socket.set_tokens(list(nse_stock_tokens.keys())[])
#     # smart_socket.connect()


# if __name__ == "__main__":
#     main()
