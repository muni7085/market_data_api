from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query

from app.routers.nse.derivatives import derivatives
from app.routers.nse.equity import equity
from app.routers.smart_api.stocks_data import (full_price_quote,
                                                partial_price_quote)
from app.routers.smart_api.utils.validator import \
    validate_symbol_and_get_token

app = FastAPI()

app.include_router(derivatives.router)
app.include_router(equity.router)


@app.get("/")
def index():
    return "This is main page"


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
