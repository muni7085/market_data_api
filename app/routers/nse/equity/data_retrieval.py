from typing import Any

from app.routers.nse.equity.data_processor import (filter_nifty_stocks,
                                                   filter_single_index,
                                                   filter_single_stock)
from app.schemas.stock_model import StockPriceInfo
from app.utils.fetch_data import fetch_nse_data
from app.utils.urls import ALL_INDICES, STOCK_URL


def get_nifty_index_stocks(url: str) -> list[StockPriceInfo]:
    """
    Fetch the price information about the stocks that are in the provided NSE index.

    Parameters:
    -----------
    url: `str`
        Url for fetching the nse index stocks data.

    Return:
    -------
    list[StockData]
        List of StockData models that contain the price information about the stocks.
    """
    nifty_fifty_socks = fetch_nse_data(url)
    return filter_nifty_stocks(nifty_fifty_socks["data"])


def get_stock_trade_info(symbol: str) -> StockPriceInfo:
    """
    Provide the price information about given stock symbol.

    Parameters:
    -----------
    symbol: `str`
        Nse stock symbol, can be obtained from the nse official website.
            eg: "SBIN","TCS" etc.

    Return:
    -------
    StockData
        StockData model contain the information about the stock.
    """
    stock_url = f"{STOCK_URL}{symbol}"
    stock_data = fetch_nse_data(stock_url)
    price_info = stock_data["priceInfo"]
    return filter_single_stock(symbol, price_info)


def get_index_data(symbol: str) -> StockPriceInfo:
    """
    Provide the price information about the Nse indices like NIFTY 50, NIFTY BANK etc.

    Parameters:
    -----------
    symbol: `str`
        Nse index symbol, can be obtained from the nse official website
            eg: "NIFTY 50","NIFTY NEXT 50" etc.

    Return:
    -------
    StockPriceInfo
        StockData model contain the information about the index
    """
    indices_data: list[dict[str, Any]] = fetch_nse_data(ALL_INDICES)["data"]
    stock_price_info: StockPriceInfo
    for index in indices_data:
        if index["index"] == symbol:
            stock_price_info = filter_single_index(index)
    return stock_price_info
