# pylint: disable=missing-function-docstring
from fastapi import FastAPI

from app.routers.nse.derivatives import derivatives
from app.routers.nse.equity import equity
from app.routers.smart_api.smart_api import smart_api

app = FastAPI()

app.include_router(derivatives.router)
app.include_router(equity.router)
app.include_router(smart_api.router)


@app.get("/", response_model=str)
def index():
    return "This is main page"
