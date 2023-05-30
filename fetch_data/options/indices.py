from .constants import BASE_URL
from .fetch_data import get_api_data


def get_option_chain_data(symbol):
    url = BASE_URL + symbol
    response = get_api_data(url, "jun")
    return response
