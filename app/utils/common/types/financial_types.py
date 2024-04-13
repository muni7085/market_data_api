from enum import Enum


class Exchange(Enum):
    NSE = "NSE"
    BSE = "BSE"


class SecurityType(Enum):
    EQUITY = "equity"
    DERIVATIVE = "derivative"
