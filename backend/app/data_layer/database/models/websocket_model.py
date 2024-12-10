"""
This module contain the schema for the InstrumentPrice table.
"""

from typing import Optional

from sqlmodel import Field, SQLModel


class InstrumentPrice(SQLModel, table=True):  # type: ignore
    """
    This class holds the information about the stock prices received from the SmartAPI socket

    Attributes
    ----------
    retrieval_timestamp: ``str``
        The timestamp representing when the data was retrieved from the socket
        Eg: "2021-09-30 10:00:00"
    last_traded_timestamp: ``str``
        The timestamp representing when the last trade was executed for the stock
        in the exchange
        Eg: "2021-09-30 09:59:59"
    symbol: ``str``
        The symbol of the equity or derivative
        Eg: "Infosys Limited"
    last_traded_price: ``str``
        The price at which the last trade was executed
        Eg: "1700.0"
    last_traded_quantity: ``str``
        The quantity of the last trade executed
        Eg: "100"
    average_traded_price: ``str``
        The average traded price for the day
        Eg: "1700.0"
    volume_trade_for_the_day: ``str``
        The total volume traded for the day
        Eg: "1000"
    total_buy_quantity: ``str``
        The total buy quantity for the day
        Eg: "500"
    total_sell_quantity: ``str``
        The total sell quantity for the day
        Eg: "500"
    """

    retrieval_timestamp: str = Field(primary_key=True)
    last_traded_timestamp: str
    symbol: str = Field(primary_key=True)
    last_traded_price: str
    last_traded_quantity: Optional[str] = None
    average_traded_price: Optional[str] = None
    volume_trade_for_the_day: Optional[str] = None
    total_buy_quantity: Optional[str] = None
    total_sell_quantity: Optional[str] = None

    def to_dict(self):
        """
        Returns the object as a dictionary
        """
        return {
            "retrieval_timestamp": self.retrieval_timestamp,
            "last_traded_timestamp": self.last_traded_timestamp,
            "symbol": self.symbol,
            "last_traded_price": self.last_traded_price,
            "last_traded_quantity": self.last_traded_quantity,
            "average_traded_price": self.average_traded_price,
            "volume_trade_for_the_day": self.volume_trade_for_the_day,
            "total_buy_quantity": self.total_buy_quantity,
            "total_sell_quantity": self.total_sell_quantity,
        }
