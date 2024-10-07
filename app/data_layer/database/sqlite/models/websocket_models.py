"""
This module contain the schema for the SocketStockPriceInfo table.
"""

from typing import Optional

from sqlmodel import Field, SQLModel


class SocketStockPriceInfo(SQLModel, table=True):
    """
    This class holds the information about the stock prices received from the SmartAPI socket

    Attributes
    ----------
    token: ``str``
        The token value for the symbol. This is the primary key
        Eg: "256265"
    retrieval_timestamp: ``str``
        The timestamp representing when the data was retrieved from the socket
        Eg: "2021-09-30 10:00:00"
    last_traded_timestamp: ``str``
        The timestamp representing when the last trade was executed for the stock
        in the exchange
        Eg: "2021-09-30 09:59:59"
    socket_name: ``str``
        The name of the socket from which the data was received
        Eg: "smartsocket"
    exchange_timestamp: ``str``
        The timestamp representing when the data was sent by the exchange
        Eg: "2021-09-30 09:59:59"
    name: ``str``
        The name of the equity or derivative
        Eg: "Infosys Limited"
    last_traded_price: ``str``
        The price at which the last trade was executed
        Eg: "1700.0"
    exchange: ``str``
        The name of the exchange where the stock is listed
        Eg: "NSE" or "BSE"
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

    token: str = Field(primary_key=True)
    retrieval_timestamp: str = Field(primary_key=True)
    last_traded_timestamp: str
    socket_name: str
    exchange_timestamp: str
    name: str
    last_traded_price: str
    exchange: Optional[str] = None
    last_traded_quantity: Optional[str] = None
    average_traded_price: Optional[str] = None
    volume_trade_for_the_day: Optional[str] = None
    total_buy_quantity: Optional[str] = None
    total_sell_quantity: Optional[str] = None

    def as_dict(self):
        """
        Returns the object as a dictionary
        """
        return {
            "token": self.token,
            "retrieval_timestamp": self.retrieval_timestamp,
            "last_traded_timestamp": self.last_traded_timestamp,
            "socket_name": self.socket_name,
            "exchange_timestamp": self.exchange_timestamp,
            "name": self.name,
            "last_traded_price": self.last_traded_price,
            "exchange": self.exchange,
            "last_traded_quantity": self.last_traded_quantity,
            "average_traded_price": self.average_traded_price,
            "volume_trade_for_the_day": self.volume_trade_for_the_day,
            "total_buy_quantity": self.total_buy_quantity,
            "total_sell_quantity": self.total_sell_quantity,
        }
