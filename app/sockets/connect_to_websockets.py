from pathlib import Path

import hydra
from omegaconf import DictConfig

from app.sockets.connections import WebsocketConnection
from app.utils.common import init_from_cfg
from app.utils.common.logger import get_logger
from app.utils.startup_utils import create_smartapi_tokens_db

logger = get_logger(Path(__file__).name)


def create_websocket_connection(cfg: DictConfig):
    num_connections = cfg.connection.num_connections

    for i in range(num_connections):
        logger.info(f"Creating connection instance {i}")
        cfg.connection.current_connection_number = i
        websocket_connection: WebsocketConnection = init_from_cfg(
            cfg.connection, WebsocketConnection
        )

        if websocket_connection:
            websocket_connection.websocket.connect(True)


@hydra.main(config_path="../configs", config_name="websocket", version_base=None)
def main(cfg):
    create_smartapi_tokens_db()
    for connection in cfg.connections:
        create_websocket_connection(connection)


if __name__ == "__main__":
    main()
