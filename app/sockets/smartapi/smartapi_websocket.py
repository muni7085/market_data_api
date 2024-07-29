from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger
from app.database.sqlite.crud.smartapi_curd import get_smartapi_tokens_by_all_conditions
from app.utils.date_utils import get_expiry_dates
from app.utils.type_utils import SymbolType
from app.database.sqlite.sqlite_db_connection import get_session
from app.utils.smartapi.data_processor import filter_tokens_by_expiry
from omegaconf import OmegaConf
import asyncio
from app.utils.connections import SmartApiConnection
from app.utils.startup_utils import create_smartapi_tokens_db
from app.database.sqlite.crud.websocket_crud import insert_socket_data_to_db
from threading import Thread

def get_tokens(name: str, instrument_type: str, exch_seg: str, num_expiries: int = 6):

    tokens = get_smartapi_tokens_by_all_conditions(
        next(get_session()),
        name=name,
        instrument_type=instrument_type,
        exch_seg=exch_seg,
    )
    if exch_seg.lower() == "nfo":
        dates = get_expiry_dates(name, SymbolType.DERIVATIVE)
        filetered_tokens = filter_tokens_by_expiry(tokens, dates[:6])
        tokens=[token.token for token in filetered_tokens]
        

    return tokens

nifty_tokens=get_tokens("NIFTY", "OPTIDX", "NFO")
banknifty_tokens=get_tokens("BANKNIFTY", "OPTIDX", "NFO")
tokens=nifty_tokens+banknifty_tokens
smartapi_connection = SmartApiConnection.get_connection()
AUTH_TOKEN = smartapi_connection.get_auth_token()
API_KEY = smartapi_connection.credentials.api_key
CLIENT_CODE = smartapi_connection.credentials.client_id
FEED_TOKEN = smartapi_connection.api.getfeedToken()

class SmartSocket(SmartWebSocketV2):
    def __init__(self, auth_token, api_key, client_code, feed_token, max_retry_attempt=2, retry_strategy=0, retry_delay=10, retry_duration=30,tokens=None,worker_id=0):
        super().__init__(auth_token, api_key, client_code, feed_token, max_retry_attempt, retry_strategy, retry_delay, retry_duration)
        self.correlation_id = "abc123"
        self.mode = 3
        self.token_list = [
            {
                "exchangeType": 2,
                "tokens": tokens
            }
        ]
        self.worker_id = worker_id
        print(len(tokens))
        print(f"Worker {self.worker_id} initialized...")
        
    
    
    def on_data(self,wsapp, message):
        logger.info("Ticks: {}".format(message))
        # close_connection()


    def on_control_message(self,wsapp, message):
        logger.info(f"Control Message: {message}")

    def on_open(self,wsapp):
        logger.info("on open...")
        some_error_condition = False
        if some_error_condition:
            error_message = "Simulated error"
            if hasattr(wsapp, 'on_error'):
                wsapp.on_error("Custom Error Type", error_message)
        else:
            super().subscribe(self.correlation_id, self.mode,self.token_list)
            # sws.unsubscribe(correlation_id, mode, token_list1)
    def on_error(self,wsapp, error):
        logger.error(error)

    def on_close(self,wsapp):
        logger.info("Close")

    def close_connection(self):
        super().close_connection()

def create_socket_connection(tokens,worker_id):
    
    correlation_id = "abc123"
    action = 1
    mode = 3
    token_list = [
        {
            "exchangeType": 2,
            "tokens": tokens
        }
    ]
    print(f"Worker {worker_id} started...")
    #retry_strategy=0 for simple retry mechanism
    sws = SmartSocket(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN,max_retry_attempt=2, retry_strategy=0, retry_delay=10, retry_duration=30,worker_id=worker_id,tokens=tokens)

    sws.connect()

threaded_connections = []
print("Total tokens: ", len(tokens))
    
for i in range(0, len(tokens), 1000):
    thread = Thread(target=create_socket_connection, args=(tokens[i:i+1000],i))
    threaded_connections.append(thread)
    thread.start()

for thread in threaded_connections:
    thread.join()
    print("Thread finished...")