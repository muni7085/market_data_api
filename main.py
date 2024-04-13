# pylint: disable=missing-function-docstring
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.database.db_connection import create_db_and_tables

from app.routers.nse.derivatives import derivatives
from app.routers.nse.equity import equity
from app.routers.smartapi.smartapi import smartapi

app = FastAPI()


app.include_router(derivatives.router)
app.include_router(equity.router)
app.include_router(smartapi.router)


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
