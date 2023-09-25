from typing import Optional
from fastapi import FastAPI
from fetch_data.options.indices import get_option_chain_data
from stocks.indices import get_index_stocks_data
from fetch_data.smart_api.stocks_data import get_stock_data
from data_provider.nse_official.stocks.nse_stocks import get_nifty_fifty_stocks
from data_provider.nse_official.models.stock_model import StockData
from data_provider.nse_official.utils.stock_urls import NIFTY_FIFTY,NIFTY_NEXT_FIFTY
from body_classes.option_chain_body import ExpiryMonth

app = FastAPI()


@app.get("/")
def index():
    return "This is main page"


@app.post("/option/{symbol}")
def option_chain(symbol: str, expiry_month: ExpiryMonth):
    return get_option_chain_data(symbol=symbol, expiry_month=expiry_month.month)


@app.get("/index/{index_name}")
def index_stocks(index_name: str, specific_stock: Optional[str] = None):
    return get_index_stocks_data(index_name, specific_stock)


@app.get("/stock/{stock_symbol}")
def stock_data(stock_symbol: str):
    return get_stock_data(stock_symbol)

@app.get("/stocks/nifty_50",response_model=list[StockData])
def nifty_fifty_stocks():
    return get_nifty_fifty_stocks(NIFTY_FIFTY)

@app.get("/stocks/nifty_next_50",response_model=list[StockData])
def nifty_fifty_stocks():
    return get_nifty_fifty_stocks(NIFTY_NEXT_FIFTY)
