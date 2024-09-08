from typing import Optional

from sqlmodel import Field, MetaData, SQLModel


class SmartAPIToken(SQLModel, table=True):
    """
    This class holds the information about the SmartAPI tokens.
    
    Attributes
    ----------
    symbol: ``str``
        The symbol of the token.
        Eg: "INFY"
    token: ``str``
        The token value for the symbol.
        Eg: "256265"
    name: ``str``
        The name of the equity or derivative.
        Eg: "Infosys Limited"
    expiry: ``str``
        The expiry date of the derivative contract.
        Applicable only for derivative instruments.
        Eg: "2021-09-30"
    strike: ``float``
        The strike price of the derivative contract.
        Eg: 1700.0
    lot_size: ``int``
        The lot size of the derivative contract.
        Eg: 100
    instrument_type: ``str``
        The type of the instrument.
        
    """

    symbol: str = Field(primary_key=True)
    token: str
    name: str
    expiry: str
    strike: Optional[float] = None
    lot_size: Optional[int] = None
    instrument_type: str
    exch_seg: str
    tick_size: Optional[float] = None
    symbol_type: Optional[str] = None 

    def to_dict(self):
        """
        Returns the object as a dictionary.
        """
        return {
            "symbol": self.symbol,
            "token": self.token,
            "name": self.name,
            "expiry": self.expiry,
            "strike": self.strike,
            "lot_size": self.lot_size,
            "instrument_type": self.instrument_type,
            "exch_seg": self.exch_seg,
            "tick_size": self.tick_size,
            "symbol_type": self.symbol_type,
        }
