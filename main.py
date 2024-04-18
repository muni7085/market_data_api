# pylint: disable=missing-function-docstring
from fastapi import FastAPI

from app.routers.nse.derivatives import derivatives
from app.routers.nse.equity import equity
from app.routers.smartapi.smartapi import smartapi

app = FastAPI()

app.include_router(derivatives.router)
app.include_router(equity.router)
app.include_router(smartapi.router)


@app.get("/", response_model=str)
def index():
    return "This is main page"
