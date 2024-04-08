# pylint: disable=missing-function-docstring
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.database.db_connection import create_db_and_tables

from app.routers.nse.derivatives import derivatives
from app.routers.nse.equity import equity
# from app.routers.authentication import authentication
from app.routers.smart_api import stocks_data

from fastapi_jwt_auth.exceptions import AuthJWTException

app = FastAPI()


app.include_router(derivatives.router)
app.include_router(equity.router)
# app.include_router(authentication.router)
app.include_router(stocks_data.router)


@app.on_event("startup")
async def startup():
    create_db_and_tables()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/authenticate", response_model=str)
def index():
    return "This is main page"
