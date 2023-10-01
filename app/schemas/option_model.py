from typing import Optional

from pydantic import BaseModel


class Option(BaseModel):
    ltp: float
    change: float
    percent_change: float
    change_in_oi: float
    percent_change_in_oi: float


class StrikePriceData(BaseModel):
    strike_price: float
    ce: Optional[Option]
    pe: Optional[Option]


class ExpiryOptionData(BaseModel):
    strike_prices: list[StrikePriceData]
    expiry_data: str
