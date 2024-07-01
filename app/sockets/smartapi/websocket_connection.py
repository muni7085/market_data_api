from app.database.sqlite.crud.smartapi_curd import get_smartapi_tokens_by_all_conditions
from app.utils.date_utils import get_expiry_dates
from app.utils.type_utils import SymbolType
from app.database.sqlite.sqlite_db_connection import get_session
from app.sockets.smartapi.smart_socket import SmartSocket
from app.utils.smartapi.data_processor import filter_tokens_by_expiry
from omegaconf import OmegaConf
from app.utils.startup_utils import create_smartapi_tokens_db
from app.database.sqlite.crud.websocket_crud import insert_socket_data_to_db

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


create_smartapi_tokens_db(True)
nifty_tokens = get_tokens("NIFTY", "OPTIDX", "NFO")
banknifty_tokens = get_tokens("BANKNIFTY", "OPTIDX", "NFO")
total_tokens = nifty_tokens | banknifty_tokens
tokens = [{"exchangeType": 2, "tokens": dict(list(total_tokens.items())[:1000])}]
cfg = OmegaConf.create(config)
smart_socket = SmartSocket.initialize_socket(
    cfg, on_data_save_callback=insert_socket_data_to_db
)
smart_socket.set_tokens(tokens)
smart_socket.connect()
