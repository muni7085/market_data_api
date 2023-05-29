from fastapi import FastAPI
from fetch_data.options.indices import get_banknifty_data

app = FastAPI()


@app.get("/")
def index():
    return "This is main page"


@app.get("/option")
def option_chain():
    return get_banknifty_data()
