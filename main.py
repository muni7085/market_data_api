from typing import Optional
from fastapi import FastAPI
from fetch_data.options.indices import get_option_chain_data
from stocks.indices import get_index_stocks_data

app = FastAPI()


@app.get("/")
def index():
    return "This is main page"


@app.get("/option/{symbol}")
def option_chain(symbol):
    return get_option_chain_data(symbol=symbol)

@app.get('/index/{index_name}')
def index_stocks(index_name: str,specific_stock: Optional[str] = None):
    return get_index_stocks_data(index_name, specific_stock)