# pylint: disable=missing-function-docstring

import uvicorn
from fastapi import FastAPI

from app.data_layer.database.db_connections import postgresql
from app.routers.authentication import authentication
from app.routers.nse.derivatives import derivatives
from app.routers.nse.equity import equity
from app.routers.smartapi.smartapi import smartapi
from app.utils.startup_utils import create_smartapi_tokens_db

app = FastAPI()

app.include_router(derivatives.router)
app.include_router(equity.router)
app.include_router(smartapi.router)
app.include_router(authentication.router)


@app.on_event("startup")
async def startup_event():
    create_smartapi_tokens_db()
    postgresql.create_db_and_tables()


@app.get("/", response_model=str)
def index():
    return "This is main page"


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
