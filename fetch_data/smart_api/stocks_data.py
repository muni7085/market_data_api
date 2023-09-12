from fetch_data.get_connection import SmartApiConnection
from fetch_data.constants import API_KEY,SYMBOLS_PATH
import http.client
import json

def get_token(symbol:str)->str:
    with open(SYMBOLS_PATH,'r') as fp:
        data=json.load(fp)
    symbol_data=data.get(symbol)
    token=None
    if symbol_data is not None:
        token=symbol_data['token']
    return token
def get_stock_data(stock_symbol:str):
    api_connection=SmartApiConnection()
    auth_token=api_connection.get_auth_token()
    conn = http.client.HTTPSConnection("apiconnect.angelbroking.com")
    stock_token=get_token(stock_symbol)
    payload = f"""{{   
        \"exchange\": \"NSE\",    
        \"tradingsymbol\": \"{stock_symbol}\",  
        \"symboltoken\":\"{stock_token}\"
    }}"""
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": "CLIENT_LOCAL_IP",
        "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
        "X-MACAddress": "MAC_ADDRESS",
        "X-PrivateKey": API_KEY,
    }
    conn.request(
        "POST", "/rest/secure/angelbroking/order/v1/getLtpData", body=payload,headers=headers
    )

    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode('utf-8'))
