from .constants import BASE_URL
from .fetch_data import get_api_data

def get_banknifty_data():
    url=BASE_URL+"BANKNIFTY"
    response=get_api_data(url,"jun")
    return response
    