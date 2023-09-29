import requests
import json
from fastapi import HTTPException
from data_provider.nse_official.utils.headers import REQUSET_HEADERS


def fetch_nse_data(url: str, max_tries: int = 1000):
    for _ in range(max_tries):
        response = requests.get(url, headers=REQUSET_HEADERS)
        stock_data = None
        if response.status_code == 200:
            stock_data = json.loads(response.content.decode("utf-8"))
            return stock_data
    raise HTTPException(
        status_code=404, detail={"Error": "Not able to get the stock data due server maintenance"}
    )
