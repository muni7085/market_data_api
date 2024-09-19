"""
This module contain the schema for the SocketStockPriceInfo table.
"""
from typing import Optional

from sqlmodel import Field, SQLModel


class SocketStockPriceInfo(SQLModel, table=True):
    """
    This class holds the information about the stock prices received from the SmartAPI socket.
    """

    token: str = Field(primary_key=True)
    retrieval_timestamp: str = Field(primary_key=True)
    last_traded_timestamp: str
    socket_name: str
    exchange_timestamp: str
    name: str
    last_traded_price: str
    last_traded_quantity: Optional[str] = None
    average_traded_price: Optional[str] = None
    volume_trade_for_the_day: Optional[str] = None
    total_buy_quantity: Optional[str] = None
    total_sell_quantity: Optional[str] = None

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
            "retrieval_timestamp": self.retrieval_timestamp,
            "last_traded_quantity": self.last_traded_quantity,
            "average_traded_price": self.average_traded_price,
            "volume_trade_for_the_day": self.volume_trade_for_the_day,
            "total_buy_quantity": self.total_buy_quantity,
            "total_sell_quantity": self.total_sell_quantity,
        }
