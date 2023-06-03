from typing import Optional
from stocks.data_cleaner import get_clean_stocks_data
import requests

def get_api_data(url: str, specific_stock: Optional[str] = None):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "authority": "www.nseindia.com",
        "scheme": "https",
    }
    response = requests.get(url,headers = header)
    if response.status_code == 200:
        response = get_clean_stocks_data(response.text,specific_stock)
        return response
    else:
        return response.headers
    
    