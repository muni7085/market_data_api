from typing import Optional
from stocks.constants import BASE_URL
from stocks.fetch_data import get_api_data

def get_index_stocks_data(index_name: str,specific_stock: Optional[str] = None):
    url = BASE_URL + index_name
    response = get_api_data(url, specific_stock)
    return response
    