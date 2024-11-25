"""
This module contains the schema for the SmartAPIToken table.
"""

from sqlmodel import Field, SQLModel


class SmartAPIToken(SQLModel, table=True):  # type: ignore
    """
    This class holds the information about the SmartAPI tokens

    Attributes
    ----------
    token: ``str``
        The token value for the symbol. This is the primary key
        Eg: "256265"
    symbol: ``str``
        The symbol of the token
        Eg: "INFY"
    name: ``str``
        The name of the equity or derivative
        Eg: "Infosys Limited"
    instrument_type: ``str``
        The type of the instrument.
        Eg: "EQ" or "OPTIDX"
    exchange: ``str``
        The exchange of the instrument where it is traded
        Eg: "NSE" or "BSE"
    expiry_date: ``str``
        The expiry date of the derivative contract. Applicable only for
        derivative instruments, means the date on which the contract expires
        Eg: "2021-09-30"
    strike_price: ``float``
        The strike price of the derivative contract
        Eg: 1700.0
    lot_size: ``int``
        The lot size of the derivative contract, means the number of shares in one lot
        Eg: 100
    tick_size: ``float``
        The tick size of the instrument, means the minimum price movement
    """

    token: str = Field(primary_key=True)
    symbol: str
    name: str
    instrument_type: str
    exchange: str
    expiry_date: str | None = None
    strike_price: float | None = None
    lot_size: int | None = None
    tick_size: float | None = None

    def to_dict(self):
        """
        Returns the object as a dictionary.
        """
        return {
            "token": self.token,
            "symbol": self.symbol,
            "name": self.name,
            "instrument_type": self.instrument_type,
            "expiry_date": self.expiry_date,
            "strike_price": self.strike_price,
            "lot_size": self.lot_size,
            "exchange": self.exchange,
            "tick_size": self.tick_size,
        }
