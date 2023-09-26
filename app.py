from typing import Annotated
from fastapi import FastAPI,Path,Query
from data_provider.nse_official.equity.nse_stocks import get_nifty_fifty_stocks,get_stock_trade_info
from data_provider.nse_official.models.stock_model import StockData
from data_provider.nse_official.utils.stock_urls import NIFTY_FIFTY,NIFTY_NEXT_FIFTY
from data_provider.nse_official.options.nse_options import get_index_option_chain


app = FastAPI()


@app.get("/")
def index():
    return "This is main page"


@app.get("/stock/{stock_symbol}")
def stock_data(stock_symbol: str):
    return get_stock_trade_info(stock_symbol)

@app.get("/stocks/nifty_50",response_model=list[StockData])
def nifty_fifty_stocks():
    return get_nifty_fifty_stocks(NIFTY_FIFTY)

@app.get("/stocks/nifty_next_50",response_model=list[StockData])
def nifty_fifty_stocks():
    return get_nifty_fifty_stocks(NIFTY_NEXT_FIFTY)

@app.get("/stock/nse/{symbol}")
def get_stock_data(symbol:Annotated[str,Path()]):
    return get_stock_trade_info(symbol)

@app.get("/option/{symbol}")
def index_option_chain(symbol:Annotated[str,Path()],expiry_date:Annotated[str,Query(example="28-Sep-2023")]):
    #TODO validate symbol and expiry date
    return get_index_option_chain(expiry_date,symbol)