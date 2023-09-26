from data_provider.nse_official.models.option_model import (
    StrikePriceData,
    ExpiryOptionData,
    Option,
)


def filter_strike_prices_with_expiry_date(records, expiry_date):
    def filterer(record):
        if record["expiryDate"] == expiry_date:
            return record
        return None

    filter_data = list(filter(filterer, records))
    return filter_data


def get_option(option):
    return {
        "ltp": option["lastPrice"],
        "change": option["change"],
        "percent_change": option["pChange"],
        "change_in_oi": option["changeinOpenInterest"],
        "percent_change_in_oi": option["pchangeinOpenInterest"],
    }


def filter_index_option(strike_prices: list[dict], expiry_date: str):
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
    return ExpiryOptionData(strike_prices=all_strike_prices, expiry_data=expiry_date)
