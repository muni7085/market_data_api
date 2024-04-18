import json
from typing import Annotated, List

from fastapi import APIRouter, Path, Query

from app.schemas.stock_model import HistoricalStockPriceInfo
from app.utils.common.types.financial_types import Exchange
from app.utils.common.types.reques_types import RequestType
from app.utils.smartapi.connection import get_endpoint_connection
from app.utils.smartapi.data_processor import process_smart_api_historical_stock_data
from app.utils.smartapi.urls import CANDLE_DATA_URL
from app.utils.smartapi.validator import (
    validate_date_range,
    validate_interval,
    validate_symbol_and_get_token,
)

router = APIRouter(prefix="/smart-api/equity", tags=["equity"])


@router.get("/history/{stock_symbol}", response_model=List[HistoricalStockPriceInfo])
async def historical_stock_data(
    stock_symbol: Annotated[str, Path()],
    interval: Annotated[
        str,
        Query(
            examples={
                "ONE_MINUTE": {
                    "value": "ONE_MINUTE",
                    "description": "Maximum 30 days one minute candlestick data is provided for one request.",
                },
                "THREE_MINUTE": {
                    "value": "THREE_MINUTE",
                    "description": "Maximum 60 days three minute candlestick data is provided for one request.",
                },
                "FIVE_MINUTE": {
                    "value": "FIVE_MINUTE",
                    "description": "Maximum 100 days five minute candlestick data is provided for one request.",
                },
                "TEN_MINUTE": {
                    "value": "TEN_MINUTE",
                    "description": "Maximum 100 days ten minute candlestick data is provided for one request.",
                },
                "FIFTEEN_MINUTE": {
                    "value": "FIFTEEN_MINUTE",
                    "description": "Maximum 200 days fifteen minute candlestick data is provided for one request.",
                },
                "THIRTY_MINUTE": {
                    "value": "THIRTY_MINUTE",
                    "description": "Maximum 200 days thirty minute candlestick data is provided for one request.",
                },
                "ONE_HOUR": {
                    "value": "ONE_HOUR",
                    "description": "Maximum 400 days one hour candlestick data is provided for one request.",
                },
                "ONE_DAY": {
                    "value": "ONE_DAY",
                    "description": "Maximum 2000 days one day candlestick data is provided for one request.",
                },
            }
        ),
    ],
    start_date: Annotated[str, Query(example="2023-09-08 12:00")],
    end_date: Annotated[str, Query(example="2023-09-09 12:00")],
):
    """
    Get the historical stock data for a given symbol.
    This endpoint provides the historical candle data of the  given stock symbol for a particular time period from an
    External API in realtime.

    Parameters:
    -----------
    - **stock_symbol**:
        It must be a valid stock symbol that is registered in the NSE website.
        eg: `TCS`, `RELIANCE`

    """

    stock_token, stock_symbol = validate_symbol_and_get_token(
        stock_exchange=Exchange.NSE, stock_symbol=stock_symbol
    )
    interval = validate_interval(interval)
    start_date, end_date = validate_date_range(
        start_date, end_date, interval, stock_symbol.split("-")[0]
    )
    payload = {
        "exchange": Exchange.NSE.value,
        "tradingsymbol": stock_symbol,
        "interval": interval,
        "fromdate": start_date,
        "todate": end_date,
        "symboltoken": stock_token,
    }
    json_payload = json.dumps(payload)

    connection = get_endpoint_connection(
        payload=json_payload,
        request_method_type=RequestType.POST,
        url=CANDLE_DATA_URL,
    )
    res = connection.getresponse()
    data = res.read()

    return process_smart_api_historical_stock_data(
        json.loads(data.decode("utf-8"))["data"]
    )
