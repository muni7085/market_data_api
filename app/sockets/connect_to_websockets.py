

import hydra
from omegaconf import DictConfig, OmegaConf
from app.sockets.socket_connections import WebsocketConnection
from app.utils.common import init_from_cfg
from app.utils.startup_utils import create_smartapi_tokens_db

def create_websocket_connection(cfg: DictConfig):
    websocket_connection:WebsocketConnection =init_from_cfg(cfg,WebsocketConnection)
    websocket_connection.websocket.connect()
    

@hydra.main(config_path="../configs", config_name="websocket", version_base=None)
def main(cfg):
    create_smartapi_tokens_db()
    for connection in cfg.connections:
        create_websocket_connection(connection)
    
if __name__ == "__main__":
    main()