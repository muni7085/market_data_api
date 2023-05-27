import json
from typing import List,Any

def get_PE_CE_data(option_type,data, is_data):
    if is_data:
        return {
            "strikePrice": data[option_type]["strikePrice"],
            "lastPrice": data[option_type]["lastPrice"],
            "change": data[option_type]["change"],
            "pChange": data[option_type]["pChange"],
            "openInterest": data[option_type]["openInterest"],
            "changeinOpenInterest": data[option_type]["changeinOpenInterest"],
            "pchangeinOpenInterest": data[option_type]["pchangeinOpenInterest"],
        }
    else:
        return {
            "strikePrice": None,
            "lastPrice": None,
            "change": None,
            "pChange": None,
            "openInterest": None,
            "changeinOpenInterest": None,
            "pchangeinOpenInterest": None,
        }

def get_expiry_based_ce_pe(expiry_list:List[str], all_data:dict[str,Any])->dict[str, dict[str, list]]:
    option_data = {expiry: {"ce": [], "pe": []} for expiry in expiry_list}
    for data in all_data:
        if data["expiryDate"] in expiry_list:
            if "CE" in data.keys():
                option_data[data["expiryDate"]]["ce"].append(get_PE_CE_data("CE", data, True))
            else:
                option_data[data["expiryDate"]]["pe"].append(get_PE_CE_data("CE", data, False))
            if "PE" in data.keys():
                option_data[data["expiryDate"]]["pe"].append(get_PE_CE_data("PE", data, True))
            else:
                option_data[data["expiryDate"]]["pe"].append(get_PE_CE_data("PE", data, False))
    return option_data

def clean_options_data(response:dict,month:str)->str:
    response=json.loads(response)
    current_month_expires=[expiry for expiry in response["records"]["expiryDates"] if month in expiry.lower()]
    if len(current_month_expires)==0:
        return {"error":"No contracts available for give month"}
    else:
        cleaned_data=get_expiry_based_ce_pe(current_month_expires,response["records"]["data"])
        return cleaned_data
    