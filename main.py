from fastapi import FastAPI

from app.routers.nse.derivatives import derivatives
from app.routers.nse.equity import equity


app = FastAPI()

app.include_router(derivatives.router)
app.include_router(equity.router)


@app.get("/")
def index():
    return "This is main page"
