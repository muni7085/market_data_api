from typing import Annotated
from fastapi import FastAPI, Path, Query, Depends, HTTPException
from data_provider.nse_official.equity.nse_stocks import (
    get_nifty_index_stocks,
    get_stock_trade_info,
)

from data_provider.models.stock_model import StockData
from data_provider.nse_official.utils.stock_urls import NIFTY_INDEX_BASE
from data_provider.nse_official.options.nse_options import (
    get_index_option_chain,
    validate_expiry_date,
)
from data_provider.nse_official.utils.validators import (
    validate_derivative_symbols,
    validate_index_symbol,
    validate_stock_symbol,
)
from data_provider.smart_api.utils.validator import validate_symbol_and_get_token

from data_provider.smart_api.stocks_data import partial_price_quote, full_price_quote

app = FastAPI()


@app.get("/")
def index():
    return "This is main page"


@app.get("/stock/nse/{stock_symbol}", dependencies=[Depends(validate_stock_symbol)])
async def get_stock_data(stock_symbol: Annotated[str, Path()]):
    return get_stock_trade_info(stock_symbol)


@app.get("/stocks/{index_symbol}", response_model=list[StockData])
async def nifty_fifty_stocks(
    index_symbol: Annotated[dict[str, str], Depends(validate_index_symbol)]
):
    index_url = f"{NIFTY_INDEX_BASE}{index_symbol}"
    return get_nifty_index_stocks(index_url)


@app.get(
    "/option/{derivative_symbol}", dependencies=[Depends(validate_derivative_symbols)]
)
async def index_option_chain(
    derivative_symbol: Annotated[str, Path()],
    expiry_date: Annotated[
        str,
        Query(
            example="28-Sep-2023",
        ),
    ],
    option_chain_type: Annotated[
        str,
        Query(
            examples={
                "stock": {"value": "stock", "description": "Option chain for stock"},
                "index": {"value": "index", "description": "option chain for index"},
            }
        ),
    ],
):
    is_date_valid = validate_expiry_date
    if not is_date_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "Error": f"{expiry_date} is not valid. It should be dd-MM-yyyy. eg, 28-Sep-2023"
            },
        )

    return get_index_option_chain(expiry_date, derivative_symbol, option_chain_type)


@app.get("/stock/smart_api/{stock_symbol}")
async def get_stock_price(
    stock_symbol: Annotated[str, Path()],
    stock_exchange: Annotated[
        str,
        Query(
            examples={
                "nse": {
                    "value": "nse",
                    "description": "get stock price quote from nse",
                },
                "bse": {
                    "value": "bse",
                    "description": "get stock price quote from bse",
                },
            }
        ),
    ],
):
    token, stock_symbol = validate_symbol_and_get_token(stock_exchange, stock_symbol)
    if token is None:
        raise HTTPException(
            status_code=400,
            detail={"Error": f"{stock_symbol} or {stock_exchange} is not valid."},
        )
    return await partial_price_quote(stock_symbol, token)


# @app.get("/stock/smart_api/{stock_symbol}")
# async def get_stock(
#     stock_symbol: Annotated[str, Path()],
#     stock_exchange: Annotated[
#         str,
#         Query(
#             examples={
#                 "NSE": {
#                     "value": "NSE",
#                     "description": "get stock price quote from NSE",
#                 },
#                 "BSE": {
#                     "value": "BSE",
#                     "description": "get stock price quote from BSE",
#                 },
#             }
#         ),
#     ],
# ):
#     token, stock_symbol = validate_symbol_and_get_token(stock_exchange, stock_symbol)
#     if token is None:
#         raise HTTPException(
#             status_code=400,
#             detail={"Error": f"{stock_symbol} or {stock_exchange} is not valid."},
#         )
#     return await full_price_quote(stock_exchange,token)
