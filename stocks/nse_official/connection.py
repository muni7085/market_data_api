import requests

def get_cookie(url:str)->str:
    response=requests.get(url)
    