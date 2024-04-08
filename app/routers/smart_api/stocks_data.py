import http.client
import json
from http.client import HTTPConnection
from app.routers.smart_api.utils.validator import validate_symbol_and_get_token
from typing import Annotated,List
from app.routers.smart_api.get_connection import SmartApiConnection
from fastapi import APIRouter, Path, Query
from app.schemas.stock_scheme import StockPriceInfo

router = APIRouter(prefix="/smart-api/equity", tags=["equity"])


def get_endpoint_connection(
    payload: str | dict, method_type: str, url: str
) -> HTTPConnection:
    api_connection = SmartApiConnection.get_connection()
    connection = http.client.HTTPSConnection("apiconnect.angelbroking.com")
    headers = api_connection.get_headers()
    connection.request(method_type, url, body=payload, headers=headers)
    return connection


async def partial_price_quote(stock_symbol: str, stock_token: str):
    payload = {
        "exchange": "NSE",
        "tradingsymbol": stock_symbol,
        "symboltoken": stock_token,
    }
    json_payload = json.dumps(payload)
    url = "/rest/secure/angelbroking/order/v1/getLtpData"
    connection = get_endpoint_connection(
        payload=json_payload, method_type="POST", url=url
    )
    res = connection.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


@router.get("history/{stock_symbol}")
def get_historical_data(
    stock_symbol: Annotated[str, Path()],
    interval: Annotated[str, Query(example="ONE_MINUTE")],
    start_date: Annotated[str,Query(example="2023-09-08 12:00")],
    end_date: Annotated[str,Query(example="2023-09-09 12:00")],
):
    stock_symbol = validate_symbol_and_get_token(
        stock_exchange="nse", stock_symbol=stock_symbol
    )[0]
    payload = {
        "exchange": "NSE",
        "symboltoken": stock_symbol,
        "interval": interval,
        "fromdate": start_date,
        "todate": end_date,
    }
    json_payload = json.dumps(payload)
    url = "/rest/secure/angelbroking/historical/v1/getCandleData"
    connection = get_endpoint_connection(
        payload=json_payload, method_type="POST", url=url
    )
    res = connection.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))
