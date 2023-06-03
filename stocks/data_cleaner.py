
import json
from typing import Optional

def filter_stocks_data(stocks_data: list)->dict[dict[str,str]]:
    filtered_stocks_data = {}
    for stock_data in stocks_data:
        filtered_stock_data = {}
        filtered_stock_data['open'] = stock_data['open']
        filtered_stock_data['day_high'] = stock_data['dayHigh']
        filtered_stock_data['day_low'] = stock_data['dayLow']
        filtered_stock_data['prev_close'] = stock_data['previousClose']
        filtered_stock_data['last_price'] = stock_data['lastPrice']
        filtered_stock_data['change'] = stock_data['change']
        filtered_stock_data['per_change'] = stock_data['pChange']
        filtered_stocks_data[stock_data['symbol']] = filtered_stock_data
    return filtered_stocks_data
        

def get_clean_stocks_data(response: str,specific_stock: Optional[str] = None) -> dict[str,dict[str,list]]:
    response_dic:dict = json.loads(response)
    index_stocks_data = {}
    index_stocks_data['advance'] = response_dic['advance']
    index_stocks_data['time'] = response_dic['timestamp']
    index_stocks_data['stocks_data'] = filter_stocks_data(response_dic['data']) 
    if specific_stock == None:
        return index_stocks_data
    else:
        return index_stocks_data['stocks_data'][specific_stock]
    