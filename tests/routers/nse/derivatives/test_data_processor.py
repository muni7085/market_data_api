# pylint: disable=missing-function-docstring
import pytest

from app.routers.nse.derivatives.data_processor import (
    filter_option_chain,
    filter_strike_prices_with_expiry_date,
    get_option,
)
from app.schemas.option_model import ExpiryOptionData


def test_filter_strike_prices_with_expiry_date(
    get_filter_strike_prices_with_expiry_date_io,
):
    for strike_prices_io in get_filter_strike_prices_with_expiry_date_io:
        option_data = strike_prices_io["input"]
        if strike_prices_io["output"] is not None:
            filtered_expiries = filter_strike_prices_with_expiry_date(*option_data)
            assert filtered_expiries == strike_prices_io["output"]
        else:
            with pytest.raises(TypeError):
                filter_strike_prices_with_expiry_date(*option_data)


def test_get_option(get_option_io):
    for option_data in get_option_io:
        options_input = option_data["input"]
        if option_data["output"] is not None:
            option_parameters = get_option(options_input)
            assert option_data["output"] == option_parameters
        else:
            with pytest.raises(KeyError):
                get_option(options_input)


def test_filter_option_chain(get_filter_option_chain_io):
    for option_data_io in get_filter_option_chain_io:
        option_data_input = option_data_io["input"]
        if option_data_io["output"] is not None:
            expiry_option_data = filter_option_chain(*option_data_input)
            assert isinstance(expiry_option_data, ExpiryOptionData)
            print(expiry_option_data.dict())
            assert expiry_option_data.dict() == option_data_io["output"]
        else:
            with pytest.raises(TypeError):
                filter_option_chain(*option_data_input)
