from data_provider.smart_api.get_connection import SmartApiConnection
import http.client
import json


def get_endpoint_connection(payload: str | dict, method_type: str, url: str):
    api_connection = SmartApiConnection()
    connection = http.client.HTTPSConnection("apiconnect.angelbroking.com")
    headers = api_connection.get_headers()
    connection.request(method_type, url, body=payload, headers=headers)
    return connection


async def partial_price_quote(stock_symbol: str, stock_token: str):
    payload = {
        "exchange": "NSE",
        "tradingsymbol": stock_symbol,
        "symboltoken": stock_token,
    }
    json_payload = json.dumps(payload)
    url = "/rest/secure/angelbroking/order/v1/getLtpData"
    connection = get_endpoint_connection(
        payload=json_payload, method_type="POST", url=url
    )
    res = connection.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


async def full_price_quote(exchange: str, stock_token: str):
    payload = {"mode": "FULL", "exchangeTokens": {exchange.upper(): [stock_token]}}
    url = "rest/secure/angelbroking/market/v1/quote/"
    connection = get_endpoint_connection(payload=payload, method_type="POST", url=url)
    res = connection.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))
