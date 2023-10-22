from typing import Any, Optional

from app.schemas.option_scheme import ExpiryOptionData, Option, StrikePriceData


def filter_strike_prices_with_expiry_date(
    records: list[dict[str, Any]], expiry_date: str
) -> list[dict[str, Any]]:
    """
    Filter the strike prices with given expiry date.
        eg: if expiry date is 28-Sep-2023 then filtered data contain strike prices information
            for that particular expiry

    Parameters:
    -----------
    records: `list`
        List contain the strike prices information.
    expiry_date: `str`
        Expiry date in "dd-MM-yyyy".

    Return:
    -------
    list
        list of stock prices data for the given expiry.
    """

    def filterer(record: dict[str, Any]) -> Optional[dict[str, Any]]:
        if record["expiryDate"] == expiry_date:
            return record
        return None

    filter_data = list(filter(filterer, records))
    return filter_data


def get_option(option: dict[str, Any]) -> dict[str, float]:
    """
    Filter the option data required to initialize `Option` model class,
    from the given "CE" or "PE" data.

    Parameters:
    -----------
    option: `dict[str, Any]`
        dictionary of either "PE" or "CE" data

    Return:
    -------
    dict[str, float]:
        dictionary contain the option data that is required to initialize `Option` model class.
    """
    return {
        "ltp": option["lastPrice"],
        "change": option["change"],
        "percent_change": option["pChange"],
        "change_in_oi": option["changeinOpenInterest"],
        "percent_change_in_oi": option["pchangeinOpenInterest"],
    }


def filter_option_chain(
    strike_prices: list[dict[str, Any]], expiry_date: str
) -> ExpiryOptionData:
    """
    Filter the index option chain data based on the expiry and required data.

    Parameters:
    -----------
    strike_prices: `list[dict[str, Any]]`
        List of strike prices data of an derivative.
    expiry_date: `str`
        Expiry date in "dd-MM-yyyy".

    Return:
    -------
    ExpiryOptionData
        This object contain all the strike prices data for a given expiry date.
    """
    all_strike_prices: list[StrikePriceData] = []
    for strike_price in strike_prices:
        ce, pe = None, None
        if "CE" in strike_price:
            ce = Option(**get_option(strike_price["CE"]))
        if "PE" in strike_price:
            pe = Option(**get_option(strike_price["PE"]))
        strike_price_data = StrikePriceData(
            strike_price=strike_price["strikePrice"], ce=ce, pe=pe
        )
        all_strike_prices.append(strike_price_data)
    return ExpiryOptionData(strike_prices=all_strike_prices, expiry_date=expiry_date)
