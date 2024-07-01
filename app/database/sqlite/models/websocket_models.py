from sqlmodel import SQLModel, Field


class WebsocketLTPData(SQLModel, table=True):
    """
    This class holds the information about the LTP data from the websocket.
    """
    timestamp:str = Field(primary_key=True)
    symbol: str
    token: str | None
    ltp: float
    open: float
    high: float
    low: float
    close: float
    last_traded_time: str
    expiry: str| None
    strike: float | None
