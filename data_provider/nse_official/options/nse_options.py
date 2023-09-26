from data_provider.nse_official.utils.fetch_data import fetch_nse_data
from data_provider.nse_official.utils.option_urls import INDEX_OPTION_CHAIN_URL
from data_provider.nse_official.options.option_data_cleaner import (
    filter_strike_prices_with_expiry_date,
    filter_index_option,
)


def get_index_option_chain(expiry_date, index):
    option_chain_url = f"{INDEX_OPTION_CHAIN_URL}{index}"
    index_option_chain_data = fetch_nse_data(option_chain_url)
    filtered_strike_price_data = filter_strike_prices_with_expiry_date(
        records=index_option_chain_data["records"]["data"], expiry_date=expiry_date
    )
    expiry_option_data = filter_index_option(filtered_strike_price_data, expiry_date)
    return expiry_option_data
