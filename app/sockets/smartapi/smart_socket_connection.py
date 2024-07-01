from app.sockets.smartapi.async_smart_socket import SmartSocket
from omegaconf import OmegaConf
from app.database.sqlite.crud.smartapi_curd import get_smartapi_tokens_by_all_conditions
from app.utils.date_utils import get_expiry_dates
from app.utils.type_utils import SymbolType
from app.database.sqlite.sqlite_db_connection import get_session
from app.utils.smartapi.data_processor import filter_tokens_by_expiry
import asyncio

config = """ 
max_retries: 5
correlation_id: smartapi01
"""


def get_tokens(name:str, instrument_type:str, exch_seg:str, num_expiries:int=6):
    
    tokens = get_smartapi_tokens_by_all_conditions(
        next(get_session()),
        name=name,
        instrument_type=instrument_type,
        exch_seg=exch_seg,
    )
    if exch_seg.lower() == "nfo":
        dates=get_expiry_dates(name,SymbolType.DERIVATIVE)
        filtered_tokens=filter_tokens_by_expiry(tokens,dates[:6])
    
    return filtered_tokens

nifty_tokens=get_tokens("NIFTY","OPTIDX","NFO")
banknifty_tokens=get_tokens("BANKNIFTY","OPTIDX","NFO")
total_tokens=nifty_tokens+banknifty_tokens


tokens = [{"exchangeType": 2, "tokens": total_tokens[:1000]}]
cfg = OmegaConf.create(config)
smart_socket = SmartSocket.initialize_socket(cfg)
smart_socket.set_tokens(tokens)
asyncio.run(smart_socket.connect(), debug=True)


