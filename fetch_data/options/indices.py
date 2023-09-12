from ..constants import BASE_URL
from .fetch_data import get_api_data
from typing import Union
from requests import Response


def get_option_chain_data(symbol:str,expiry_month:str)->Union[dict,Response]:
    url = BASE_URL + symbol
    response = get_api_data(url, expiry_month)
    return response
