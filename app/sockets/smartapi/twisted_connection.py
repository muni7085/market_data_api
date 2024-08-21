
from app.sockets.smartapi.smart_twisted_socket import SmartApiTicker
from omegaconf import OmegaConf
from app.database.sqlite.crud.smartapi_curd import get_smartapi_tokens_by_all_conditions
from app.utils.startup_utils import create_smartapi_tokens_db
from app.utils.date_utils import get_expiry_dates
from app.utils.type_utils import SymbolType
from app.database.sqlite.sqlite_db_connection import get_session
from app.utils.smartapi.data_processor import filter_tokens_by_expiry
import asyncio
import threading
from queue import Queue

config = """ 
max_retries: 5
correlation_id: smartapi01
"""


def get_tokens(symbol_type):
    tokens = get_smartapi_tokens_by_all_conditions(
        next(get_session()),
        symbol_type=symbol_type
    )
    # if exch_seg.lower() == "nfo":
    #     dates = get_expiry_dates(name, SymbolType.DERIVATIVE)
    #     filtered_tokens = filter_tokens_by_expiry(tokens, dates[:6])
    #     tokens = {token.token: token.symbol for token in filtered_tokens}
    return {token.token:token.name for token in tokens}


def instantiate_smart_socket(tokens, id, queue):
    print("starting thread", id)
    cfg = OmegaConf.create(config)
    cfg["thread_id"] = id
    smart_socket = SmartApiTicker.initialize_socket(cfg, queue)
    smart_socket.set_tokens(tokens)
    # asyncio.run(smart_socket.connect(), debug=True)
    smart_socket.connect(threaded=True)


# Create the shared queue
queue = Queue()

# Create 3 threads and start them
threads = []
max_tokens_per_instance = 1
create_smartapi_tokens_db(True)
total_tokens = get_tokens("EQ")
# banknifty_tokens = get_tokens("BANKNIFTY", "OPTIDX", "NFO")
# total_tokens = nifty_tokens | banknifty_tokens
# SmartApiTicker.token_map = total_tokens

tokens = [
    {
        "exchangeType": 1,
        "tokens": dict(
            list(total_tokens.items())[
                :1000
            ]
        ),
    }
]
    
instantiate_smart_socket(tokens, 1, queue)