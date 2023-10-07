from pydantic import BaseModel


class StockPriceInfo(BaseModel):
    """
    StockPriceInfo model represents the stock price information of a stock
    """

    symbol: str
    last_traded_price: float
    day_open: float
    day_low: float
    day_high: float
    change: float
    percent_change: float
