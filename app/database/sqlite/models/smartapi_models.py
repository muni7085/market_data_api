from typing import Optional

from sqlmodel import Field, SQLModel


class SmartAPIToken(SQLModel, table=True):
    """
    This class holds the information about the SmartAPI tokens.
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
        }
