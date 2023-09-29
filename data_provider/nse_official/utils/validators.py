from functools import lru_cache
from typing import Annotated

from fastapi import HTTPException, Path
from data_provider.nse_official.utils.common_urls import (
    NSE_INDEX_SYMBOLS,
    NSE_STOCK_SYMBOLS,
    NSE_F_AND_O_SYMBOLS
)
from data_provider.utils.file_utls import get_symbols





def validate_stock_symbol(stock_symbol: str):
    symbols = set(get_symbols(NSE_STOCK_SYMBOLS)["symbols"])
    if stock_symbol not in symbols:
        raise HTTPException(
            status_code=404,
            detail={
                "Error": f"{stock_symbol} is not a valid stock symbol. "
                + "Please refer nse official website to get stock symbols"
            },
        )


def validate_index_symbol(index_symbol: Annotated[str, Path()]):
    symbols = get_symbols(NSE_INDEX_SYMBOLS)
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
    all_derivative_symbols = get_symbols(NSE_F_AND_O_SYMBOLS)
    if derivative_symbol not in all_derivative_symbols:
        raise HTTPException(
            status_code=404,
            detail={
                "Error": f"{derivative_symbol} is not a valid index symbol. "
                + "Please refer nse official website to get index symbols"
            },
        )
