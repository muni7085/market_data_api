from app.database.sqlite.crud.smartapi_curd import get_smartapi_tokens_by_all_conditions
from app.database.sqlite.sqlite_db_connection import get_session
from app.sockets.smartapi.smart_socket import SmartSocket


def get_all_stock_tokens(symbol_type: str = None, exch_seg: str = None):

    smartapi_tokens=get_smartapi_tokens_by_all_conditions(
        next(get_session()), symbol_type=symbol_type, exch_seg=exch_seg
    )
    tokens=[token.token for token in smartapi_tokens]

    return tokens

nse_stock_tokens=get_all_stock_tokens(symbol_type="EQ", exch_seg="NSE")

cfg={
    "mode": 3,
    "correlation_id": "smartapi00",
    "exchange_type": 1,
    "subscription_mode": 3,
    "worker_id": 0
}

smart_socket=SmartSocket.initialize_socket(cfg)
smart_socket.set_tokens(nse_stock_tokens[:1000])
smart_socket.connect()

