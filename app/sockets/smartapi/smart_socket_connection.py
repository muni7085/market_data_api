from app.sockets.smartapi.async_smart_socket import SmartSocket
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


def get_tokens(name: str, instrument_type: str, exch_seg: str, num_expiries: int = 6):
    tokens = get_smartapi_tokens_by_all_conditions(
        next(get_session()),
        name=name,
        instrument_type=instrument_type,
        exch_seg=exch_seg,
    )
    if exch_seg.lower() == "nfo":
        dates = get_expiry_dates(name, SymbolType.DERIVATIVE)
        filtered_tokens = filter_tokens_by_expiry(tokens, dates[:6])
        tokens = {token.token: token.symbol for token in filtered_tokens}
    return tokens


def instantiate_smart_socket(tokens, id, queue):
    print("starting thread", id)
    cfg = OmegaConf.create(config)
    cfg["thread_id"] = id
    smart_socket = SmartSocket.initialize_socket(cfg, queue)
    smart_socket.set_tokens(tokens)
    asyncio.run(smart_socket.connect(), debug=True)


# Create the shared queue
queue = Queue()

# Create 3 threads and start them
threads = []
max_tokens_per_instance = 10
create_smartapi_tokens_db(True)
nifty_tokens = get_tokens("NIFTY", "OPTIDX", "NFO")
banknifty_tokens = get_tokens("BANKNIFTY", "OPTIDX", "NFO")
total_tokens = nifty_tokens | banknifty_tokens
SmartSocket.token_map = total_tokens
for i in range(1):
    tokens = [
        {
            "exchangeType": 2,
            "tokens": dict(
                list(total_tokens.items())[
                    i * max_tokens_per_instance : (i + 1) * max_tokens_per_instance
                ]
            ),
        }
    ]
    thread = threading.Thread(target=instantiate_smart_socket, args=(tokens, i, queue))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()
