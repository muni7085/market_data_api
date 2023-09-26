
from data_provider.nse_official.equity.stock_data_cleaner import filter_nifty_stocks,filter_single_stock
from data_provider.nse_official.utils.stock_urls import STOCK_URL
from data_provider.nse_official.utils.fetch_data import fetch_nse_data



def get_nifty_fifty_stocks(url:str):
    nifty_fifty_socks=fetch_nse_data(url)
    return filter_nifty_stocks(nifty_fifty_socks["data"])

def get_stock_trade_info(symbol:str):
    #TODO check the correctness of the symbol
    stock_url=f"{STOCK_URL}{symbol}"
    stock_data=fetch_nse_data(stock_url)
    price_info=stock_data["priceInfo"]
    return filter_single_stock(symbol,price_info)
    
