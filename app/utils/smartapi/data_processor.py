from typing import Any, Dict

from app.schemas.stock_model import SmartAPIStockPriceInfo


def process_smart_api_stock_data(
    stock_price_data: Dict[str, Any]
) -> SmartAPIStockPriceInfo:
    """
    Processes the data from the SmartAPI and returns the processed data

    Parameters:
    -----------
    stock_price_data: ``Dict[str, Any]``
        The data from the SmartAPI to be processed

    Returns:
    --------
    ``SmartAPIStockPriceInfo``
        The processed data from the SmartAPI as a SmartAPIStockPriceInfo object

    """
    return SmartAPIStockPriceInfo(
        symbol=stock_price_data["tradingsymbol"],
        last_traded_price=stock_price_data["ltp"],
        day_open=stock_price_data["open"],
        day_low=stock_price_data["low"],
        day_high=stock_price_data["high"],
        change=stock_price_data["ltp"] - stock_price_data["close"],
        percent_change=(
            (stock_price_data["ltp"] - stock_price_data["close"])
            / stock_price_data["close"]
        )
        * 100,
        symbol_token=stock_price_data["symboltoken"],
        prev_day_close=stock_price_data["close"],
    )
