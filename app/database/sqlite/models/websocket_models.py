from sqlmodel import SQLModel, Field
from typing import Optional



class SocketStockPriceInfo(SQLModel,table=True):
    """
    This class holds the information about the stock prices received from the SmartAPI socket.
    """
    last_traded_timestamp: str
    token: str = Field(primary_key=True)
    socket_name: str
    retrival_timestamp: str= Field(primary_key=True)
    exchange_timestamp: str
    name: str
    last_traded_price: str
    high_price_of_the_day: Optional[str] = None
    low_price_of_the_day: Optional[str] = None
    open_price_of_the_day: Optional[str] = None
    closed_price: Optional[str] = None
    last_traded_quantity: Optional[str] = None
    average_traded_price: Optional[str] = None
    volume_trade_for_the_day: Optional[str] = None
    total_buy_quantity: Optional[str] = None
    total_sell_quantity: Optional[str] = None
    open_interest: Optional[str] = None
    open_interest_change_percentage: Optional[str] = None
    
    def as_dict(self):
        """
        Returns the object as a dictionary.
        """
        return {
            "last_traded_timestamp": self.last_traded_timestamp,
            "token": self.token,
            "exchange_timestamp": self.exchange_timestamp,
            "name": self.name,
            "last_traded_price": self.last_traded_price,
            "high_price_of_the_day": self.high_price_of_the_day,
            "retrival_timestamp": self.retrival_timestamp,
            "low_price_of_the_day": self.low_price_of_the_day,
            "open_price_of_the_day": self.open_price_of_the_day,
            "closed_price": self.closed_price,
            "last_traded_quantity": self.last_traded_quantity,
            "average_traded_price": self.average_traded_price,
            "volume_trade_for_the_day": self.volume_trade_for_the_day,
            "total_buy_quantity": self.total_buy_quantity,
            "total_sell_quantity": self.total_sell_quantity,
            "open_interest": self.open_interest,
            "open_interest_change_percentage": self.open_interest_change_percentage,
        }
        
