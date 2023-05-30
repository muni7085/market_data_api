import json
from typing import List, Any


def get_PE_CE_data(option_type: str, data: dict, is_data: bool) -> dict[str, list]:
    """
    if CE or PE data is present then returns the data in dict format else returns dict with `0` values

    Parameters
    ----------
        option_type: ``str``
            CE or PE
        data: ``str``
            CE or PE data
        is_data: ``bool``
            is data available or not means is there any contract at that strike price

    Returns
    -------
        filtered_data: ``dict[str, list]``
            cleaned data for given option type
    """
    if is_data:
        filtered_data = {
            "strikePrice": data[option_type]["strikePrice"],
            "lastPrice": data[option_type]["lastPrice"],
            "change": data[option_type]["change"],
            "pChange": data[option_type]["pChange"],
            "openInterest": data[option_type]["openInterest"],
            "changeinOpenInterest": data[option_type]["changeinOpenInterest"],
            "pchangeinOpenInterest": data[option_type]["pchangeinOpenInterest"],
        }
    else:
        filtered_data = {
            "strikePrice": None,
            "lastPrice": None,
            "change": None,
            "pChange": None,
            "openInterest": None,
            "changeinOpenInterest": None,
            "pchangeinOpenInterest": None,
        }
    return filtered_data


def get_expiry_based_ce_pe(
    expiry_list: List[str], all_data: List[dict]
) -> dict[str, dict[str, list]]:
    """
    filters the data based on the given list of expiry dates

    Parameters
    ----------
        expiry_list: ``List[str]``
            list of expiry dates in dd-MM-yyyy format
            eg: 25-Jun-2023
        all_data: ``dict[str, Any]``
            api response data from nse in dict format

    Returns
    -------
        option_data: ``dict[str, dict[str, list]]``
            cleaned data for given expiry dates
    """
    option_data: dict = {expiry: {"ce": [], "pe": []} for expiry in expiry_list}
    for data in all_data:
        if data["expiryDate"] in expiry_list:
            if "CE" in data.keys():
                option_data[data["expiryDate"]]["ce"].append(
                    get_PE_CE_data("CE", data, True)
                )
            else:
                option_data[data["expiryDate"]]["pe"].append(
                    get_PE_CE_data("CE", data, False)
                )
            if "PE" in data.keys():
                option_data[data["expiryDate"]]["pe"].append(
                    get_PE_CE_data("PE", data, True)
                )
            else:
                option_data[data["expiryDate"]]["pe"].append(
                    get_PE_CE_data("PE", data, False)
                )
    return option_data


def clean_options_data(response: str, month: str) -> dict[str, dict[str, list]]:
    """
    clean the api response from NSE, to get given month expiry (weekly) contracts and
    response contains dictionary of expiry data as key and values as ce and pe list of dicts
    with `strikePrice`, `lastPrice`, `change`, `pChange`, `openInterest`, `changeinOpenInterest`, `pchangeinOpenInterest`

    Parameters
    ----------
        response: ``dict``
            api response data from nse
        month: ``str``
            month name to filter contracts eg: Jan, Feb etc..

    Returns
    -------
        cleaned: ``dict[str, dict[str, list]]``
            dictionary of expiry and their ce, pe data
    """
    response_dict: dict = json.loads(response)
    current_month_expires = [
        expiry
        for expiry in response_dict["records"]["expiryDates"]
        if month in expiry.lower()
    ]
    if len(current_month_expires) == 0:
        return {"error": "No contracts available for give month"}
    else:
        cleaned_data = get_expiry_based_ce_pe(
            current_month_expires, response_dict["records"]["data"]
        )
        return cleaned_data
