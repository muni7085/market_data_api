from app.sockets.smartapi.smart_socket import SmartSocket
from omegaconf import OmegaConf
import json

config=""" 
max_retries: 5
correlation_id: smartapi01
"""
tokens = [
    {
        "exchangeType": 1,
        "tokens": ["11536"],
    }
]
cfg=OmegaConf.create(config)
smart_socket=SmartSocket.initialize_socket(cfg)
smart_socket.set_tokens(tokens)
smart_socket.connect()


