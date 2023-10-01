from typing import Annotated

from fastapi import HTTPException, Path
from core.utils.urls import (
    NSE_INDEX_SYMBOLS,
    NSE_STOCK_SYMBOLS,
    NSE_F_AND_O_SYMBOLS,
)
from core.utils.file_utls import get_symbols


months = {
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
}


def validate_stock_symbol(stock_symbol: str):
    """
    validate stock symbol with the available stock symbols in the Nse official website

    Parameters:
    -----------
    stock_symbol: `str`
        stock symbol to be validated
            eg: "TCS", "INFY", etc.

    Raises:
    -------
    HTTPException:
        Raises when the stock symbol is not available in the Nse official website
    """
    symbols = set(get_symbols(NSE_STOCK_SYMBOLS)["symbols"])
    if stock_symbol not in symbols:
        raise HTTPException(
            status_code=404,
            detail={
                "Error": f"{stock_symbol} is not a valid stock symbol. "
                + "Please refer nse official website to get stock symbols"
            },
        )


def validate_index_symbol(index_symbol: Annotated[str, Path()]) -> str:
    """
    Validate index symbol with the available index symbols in the Nse official website.

    Parameters:
    -----------
    index_symbol: `Annotated[str, Path()]`
        index symbol to be validated
            eg: "NIFTY 50","NIFTY 100", etc.

    Raises:
    -------
    HTTPException:
        Raises when the index symbol is not available in the Nse official website.

    Return:
    -------
    `str`
        Url path to the index symbol endpoint.
    """
    symbols = get_symbols(NSE_INDEX_SYMBOLS)
    print(index_symbol)
    if index_symbol not in symbols:
        raise HTTPException(
            status_code=404,
            detail={
                "Error": f"{index_symbol} is not a valid index symbol. "
                + "Please refer nse official website to get index symbols"
            },
        )
    return symbols[index_symbol]


def validate_derivative_symbols(derivative_symbol: str):
    """
    Validate derivative symbol with the available derivative symbols in the Nse official website.

    Parameters:
    -----------
    derivative_symbol: `str`
        derivative symbol to be validated
         eg: "NIFTY", "ABB", etc.

    Raises:
    -------
    HTTPException:
        Raises when the derivative symbol is not available in the Nse official website.
    """
    all_derivative_symbols = get_symbols(NSE_F_AND_O_SYMBOLS)
    if derivative_symbol not in all_derivative_symbols:
        raise HTTPException(
            status_code=404,
            detail={
                "Error": f"{derivative_symbol} is not a valid index symbol. "
                + "Please refer nse official website to get index symbols"
            },
        )


def validate_expiry_date(expiry_data: str) -> bool:
    """
    Validate the given expiry date to ensure that the given date is in "dd-MM-yyyy" format.

    Parameters:
    -----------
    expiry_data: `str`
        expiry date to be validated.

    Return:
    -------
    bool
        whether the given date is valid or not.
    """
    day, mon, _ = expiry_data.split("-")
    if mon not in months or day > 31:
        return False
    return True
