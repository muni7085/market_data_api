import requests
import json
from .data_cleaner import clean_options_data


def get_api_data(url: str, month: str):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "authority": "www.nseindia.com",
        "scheme": "https",
    }

    response = requests.get(url, headers=header)
    if response.status_code == 200:
        response = response.text
        return clean_options_data(response_dict=response, month=month)
    else:
        return response.headers
