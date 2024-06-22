from app.sockets.smartapi.async_smart_socket import SmartSocket
from omegaconf import OmegaConf
import json
import asyncio

config=""" 
max_retries: 5
correlation_id: smartapi01
"""

def get_tokens(num):
    with open(
        "/home/munikumar-17774/Desktop/projects/python_projects/market_data_api/app/data/smart_api/nse_symbols.json",
        "r",
    ) as fp:
        data = json.load(fp)
        tokens = [val for key, val in data.items()]
    return list(map(str,tokens[:num]))
tokens = [
    {
        "exchangeType": 1,
        "tokens": get_tokens(10)
    }
]
cfg=OmegaConf.create(config)
smart_socket=SmartSocket.initialize_socket(cfg)
smart_socket.set_tokens(tokens)
asyncio.run(smart_socket.connect(),debug=True)


