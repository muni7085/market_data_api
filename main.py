from fastapi import FastAPI
from fetch_data.options.indices import get_option_chain_data

app = FastAPI()


@app.get("/")
def index():
    return "This is main page"


@app.get("/option/{symbol}")
def option_chain(symbol):
    return get_option_chain_data(symbol=symbol)
