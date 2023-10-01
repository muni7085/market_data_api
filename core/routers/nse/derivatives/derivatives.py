from core.schemas.option_model import ExpiryOptionData
from core.routers.nse.utils.fetch_data import fetch_nse_data
from core.routers.nse.utils.urls import INDEX_OPTION_CHAIN_URL, STOCK_OPTION_CHAIN_URL
from core.routers.nse.derivatives.derivatives_data_cleaner import (
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


def get_index_option_chain(
    expiry_date: str, derivative_symbol: str, derivative_type: str
) -> ExpiryOptionData:
    """
    Fetch the option chain data of the given symbol from the Nse Website.

    Parameters:
    -----------
    expiry_date: `str`
        Option expiry date in "dd-MM-yyyy" format.
            eg: 28-Sep-2023
    derivative_symbol: `str`
        derivative symbol to get the option chain.
    derivative_type: `str`
        The derivative type that is either "stock" or "index"

    Return:
    -------
    ExpiryOptionData
        Option expiry data that contains the option chain information about the given derivative.
    """
    base_url = INDEX_OPTION_CHAIN_URL

    if derivative_type == "stock":
        base_url = STOCK_OPTION_CHAIN_URL

    option_chain_url = f"{base_url}{derivative_symbol}"
    index_option_chain_data = fetch_nse_data(option_chain_url)
    filtered_strike_price_data = filter_strike_prices_with_expiry_date(
        records=index_option_chain_data["records"]["data"], expiry_date=expiry_date
    )
    expiry_option_data = filter_index_option(filtered_strike_price_data, expiry_date)

    return expiry_option_data


def validate_expiry_date(expiry_data: str) -> bool:
    """
    Validate the given expiry date to ensure that the given date is in "dd-MM-yyyy" format.

    Parameters:
    -----------
    expiry_data: `str`
        expiry date to be validated.

    Return:
    -------
    bool
        whether the given date is valid or not.
    """
    day, mon, _ = expiry_data.split("-")
    if mon not in months or day > 31:
        return False
    return True
