import requests
import json
from data_provider.nse_official.utils.headers import REQUSET_HEADERS
from data_provider.nse_official.stocks.data_cleaner import filter_nifty_stocks
from data_provider.nse_official.utils.stock_urls import NIFTY_FIFTY


def get_nifty_stocks(url:str):
    response=requests.get(url,headers=REQUSET_HEADERS)
    clean_data=None
    if response.status_code==200:
        raw_stocks_data=json.loads(response.content.decode("utf-8"))
        clean_data=filter_nifty_stocks(raw_stocks_data["data"])
    return clean_data

def get_nifty_fifty_stocks(url:str):
    while True:
        nifty_fifty_socks=get_nifty_stocks(url)
        if nifty_fifty_socks:
            break
    return nifty_fifty_socks
