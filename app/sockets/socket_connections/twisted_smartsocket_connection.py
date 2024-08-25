from app.database.sqlite.crud.smartapi_curd import get_smartapi_tokens_by_all_conditions
from app.database.sqlite.sqlite_db_connection import get_session
from app.sockets.smartapi.smart_twisted_socket import SmartApiTicker
from app.utils.common.logger import get_logger
from pathlib import Path
import hydra
logger=get_logger(Path(__file__).name)


def get_all_stock_tokens(symbol_type: str = None, exch_seg: str = None):

    smartapi_tokens=get_smartapi_tokens_by_all_conditions(
        next(get_session()), symbol_type=symbol_type, exch_seg=exch_seg
    )
    tokens=[token.token for token in smartapi_tokens]

    return tokens

def on_data_save_callback(kafka_topic,kafka_producer,data):
    try:
        kafka_producer.send(kafka_topic,value=data)
        return True
    except Exception as e:
        logger.error(f"Error while sending data to kafka: {e}")
        return False

@hydra.main(config_path="../../configs/socket",config_name="smartsocket")
def main(cfg):
    
    nse_stock_tokens=get_all_stock_tokens(symbol_type="EQ", exch_seg="NSE")
    

    smart_socket=SmartApiTicker.initialize_socket(cfg)
    smart_socket.set_tokens(nse_stock_tokens[:1000])
    smart_socket.connect()

