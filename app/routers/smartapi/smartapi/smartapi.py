import json
from typing import Annotated

from fastapi import APIRouter, Path

from app.schemas.stock_model import SmartAPIStockPriceInfo
from app.utils.common.types.financial_types import Exchange
from app.utils.common.types.reques_types import RequestType
from app.utils.smartapi.connection import get_endpoint_connection
from app.utils.smartapi.data_processor import process_smart_api_stock_data
from app.utils.smartapi.urls import LAST_TRADED_PRICE_URL
from app.utils.smartapi.validator import validate_symbol_and_get_token
from app.utils.common.exceptions import UnkownException

router = APIRouter(prefix="/smart-api/equity", tags=["equity"])


@router.get("/price/{stock_symbol}", response_model=SmartAPIStockPriceInfo)
async def latest_price_quote(stock_symbol: Annotated[str, Path()]):
    """
    Get the stock data for a given symbol.
    This endpoint provides the latest trade information for the stock symbol from an External API in realtime.

    Parameters:
    -----------
    - **stock_symbol**:
        It must be a valid stock symbol that is registered in the NSE website.
        eg: `TCS`, `RELIANCE`

    """

    stock_token, stock_symbol = validate_symbol_and_get_token(
        stock_exchange=Exchange.NSE, stock_symbol=stock_symbol
    )
    payload = {
        "exchange": Exchange.NSE.value,
        "tradingsymbol": stock_symbol,
        "symboltoken": stock_token,
    }
    json_payload = json.dumps(payload)

    connection = get_endpoint_connection(
        payload=json_payload,
        request_method_type=RequestType.POST,
        url=LAST_TRADED_PRICE_URL,
    )
    res = connection.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    
    if not data["data"]:
        raise UnkownException(error_message=data["message"], status_code=res.status)

    return process_smart_api_stock_data(data["data"])
