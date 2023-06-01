from fastapi import FastAPI
from fetch_data.options.indices import get_option_chain_data
from body_classes.option_chain_body import ExpiryMonth
app = FastAPI()


@app.get("/")
def index():
    return "This is main page"


@app.post("/option/{symbol}")
def option_chain(symbol:str, expiry_month:ExpiryMonth):
    return get_option_chain_data(symbol=symbol,expiry_month=expiry_month.month)
