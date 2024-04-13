from typing import Tuple

from app.utils.common.exceptions import SymbolNotFoundException
from app.utils.common.types.financial_types import Exchange
from app.utils.file_utils import get_symbols
from app.utils.smartapi.constants import BSE_SYMBOLS_PATH, NSE_SYMBOLS_PATH


def validate_symbol_and_get_token(
    stock_exchange: Exchange, stock_symbol: str
) -> Tuple[str, str]:
    """
    Validate the stock symbol and get the stock token from the symbols data.
    Ref this for all the symbols: https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json

    Parameters:
    -----------
    stock_exchange: ``Exchange``
        The stock exchange of the stock symbol
    stock_symbol: ``str``
        The stock symbol to be validated and get the token

    Raises:
    -------
    ``SymbolNotFoundException``
        If the stock symbol is not found in the symbols data

    Returns:
    --------
    Tuple[str, str]
        The stock token and the stock symbol

    """
    symbols_path = BSE_SYMBOLS_PATH

    if stock_exchange == Exchange.NSE:
        symbols_path = NSE_SYMBOLS_PATH
        stock_symbol = stock_symbol.upper() + "-EQ"

    all_symbols_data = get_symbols(symbols_path)

    if stock_symbol not in all_symbols_data:
        raise SymbolNotFoundException(stock_symbol.split("-")[0])

    return all_symbols_data[stock_symbol], stock_symbol
