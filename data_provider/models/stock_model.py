from pydantic import BaseModel
class StockData(BaseModel):
    symbol:str
    last_price:float
    day_open:float
    day_low:float
    day_high:float
    change:float
    pchange:float
    
    