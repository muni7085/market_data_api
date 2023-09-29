from data_provider.models.option_model import ExpiryOptionData
from data_provider.nse_official.utils.fetch_data import fetch_nse_data
from data_provider.nse_official.utils.option_urls import INDEX_OPTION_CHAIN_URL,STOCK_OPTION_CHAIN_URL
from data_provider.nse_official.options.option_data_cleaner import (
    filter_strike_prices_with_expiry_date,
    filter_index_option,
)

months = {
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
}


def get_index_option_chain(expiry_date:str, index:str,option_chain_type:str)->ExpiryOptionData:
    base_url=INDEX_OPTION_CHAIN_URL
    if option_chain_type=="stock":
        base_url=STOCK_OPTION_CHAIN_URL
    option_chain_url = f"{base_url}{index}"
    index_option_chain_data = fetch_nse_data(option_chain_url)
    filtered_strike_price_data = filter_strike_prices_with_expiry_date(
        records=index_option_chain_data["records"]["data"], expiry_date=expiry_date
    )
    expiry_option_data = filter_index_option(filtered_strike_price_data, expiry_date)
    return expiry_option_data


def validate_expiry_date(expiry_data):
    day,mon,_=expiry_data.split("-")
    if mon not in months or day>31:
        return False
    return True

