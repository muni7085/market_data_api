# pylint: disable=missing-function-docstring
from fastapi import FastAPI
from app.database.db_connection import create_db_and_tables

from app.routers.nse.derivatives import derivatives
from app.routers.nse.equity import equity
from app.routers.authentication import authentication

app = FastAPI()

app.include_router(derivatives.router)
app.include_router(equity.router)
app.include_router(authentication.router)



@app.on_event("startup")
async def startup():
    create_db_and_tables()


@app.get("/authenticate", response_model=str)
def index():
    return "This is main page"
