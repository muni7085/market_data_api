from data_provider.nse_official.models.stock_model import StockData


def filter_nifty_stocks(raw_stocks_data):
    filtered_stocks_data = []
    for raw_stock_data in raw_stocks_data:
        stock_data = StockData(
            symbol=raw_stock_data["symbol"],
            last_price=raw_stock_data["lastPrice"],
            day_open=raw_stock_data["open"],
            day_low=raw_stock_data["dayLow"],
            day_high=raw_stock_data["dayHigh"],
            change=raw_stock_data["change"],
            pchange=raw_stock_data["pChange"],
        )
        filtered_stocks_data.append(stock_data)
    return filtered_stocks_data


def filter_single_stock(symbol: str, raw_stock_data: dict):
    return StockData(
        symbol=symbol,
        last_price=raw_stock_data["lastPrice"],
        day_open=raw_stock_data["open"],
        day_high=raw_stock_data["intraDayHighLow"]["max"],
        day_low=raw_stock_data["intraDayHighLow"]["min"],
        change=raw_stock_data["change"],
        pchange=raw_stock_data["pChange"],
    )
