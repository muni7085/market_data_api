# pylint: disable=missing-function-docstring
from fastapi import FastAPI

from app.routers.nse.derivatives import derivatives
from app.routers.nse.equity import equity
from app.routers.smartapi.smartapi import smartapi
from app.utils.startup_utils import create_smartapi_tokens_db
from app.routers.authentication import authentication

app = FastAPI()

app.include_router(derivatives.router)
app.include_router(equity.router)
app.include_router(smartapi.router)
app.include_router(authentication.router)


@app.on_event("startup")
async def startup_event():
    create_smartapi_tokens_db()


@app.get("/", response_model=str)
def index():
    return "This is main page"
