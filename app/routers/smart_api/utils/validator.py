from typing import Optional

from app.routers.smart_api.utils.constants import (BSE_SYMBOLS_PATH,
                                                    NSE_SYMBOLS_PATH)
from app.utils.file_utils import get_symbols


def validate_symbol_and_get_token(
    stock_exchange: str, stock_symbol: str
) -> Optional[str]:
    symbols_path = BSE_SYMBOLS_PATH
    if stock_exchange == "nse":
        symbols_path = NSE_SYMBOLS_PATH
        stock_symbol = stock_symbol.upper() + "-EQ"
    print(stock_symbol)
    all_symbols_data = get_symbols(symbols_path)
    if stock_symbol not in all_symbols_data:
        return None, None
    return all_symbols_data[stock_symbol], stock_symbol
