from fetch_data.get_connection import SmartApiConnection
from fetch_data.constants import API_KEY, SYMBOLS_PATH
import http.client
import json


def get_token(symbol: str) -> str:
    """
    Retrieve the token value for the given symbol
    Parameters
    ----------
    symbol: ``str``
        Stock symbol `eg:` LT-EQ

    Returns
    -------
    RetName: ``str``
        Token value corresponding to the symbol from the angle one API
    """
    with open(SYMBOLS_PATH, "r") as fp:
        data = json.load(fp)
    symbol_data = data.get(symbol)
    token = None

    if symbol_data is not None:
        token = symbol_data["token"]

    return token


def get_stock_data(stock_symbol: str):
    api_connection = SmartApiConnection()
    conn = http.client.HTTPSConnection("apiconnect.angelbroking.com")
    stock_token = get_token(stock_symbol)
    payload = f"""{{   
        \"exchange\": \"NSE\",    
        \"tradingsymbol\": \"{stock_symbol}\",  
        \"symboltoken\":\"{stock_token}\"
    }}"""
    headers = api_connection.get_headers()
    conn.request(
        "POST",
        "/rest/secure/angelbroking/order/v1/getLtpData",
        body=payload,
        headers=headers,
    )
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))
