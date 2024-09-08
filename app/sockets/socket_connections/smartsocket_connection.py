from app.sockets.socket_connections.websocket_connection import WebsocketConnection
from app.database.sqlite.crud.smartapi_curd import get_smartapi_tokens_by_all_conditions
from typing import Dict, List
from app.sockets.tiwsted_sockets.smartsocket import SmartSocket
from app.utils.common.logger import get_logger
from functools import partial
from kafka import KafkaProducer
import hydra
from omegaconf import DictConfig
from app.utils.smartapi.validator import validate_symbol_and_get_token
from pathlib import Path
from app.sockets.websocket_datahandler.on_data_callbacks.base_callback import (
    BaseCallback,
)
from app.utils.common.types.financial_types import Exchange
from app.utils.smartapi.smartsocket_types import ExchangeType
from app.utils.common import init_from_cfg
from app.utils.common.exceptions import SymbolNotFoundException

logger = get_logger(Path(__file__).name)



@WebsocketConnection.register("smartsocket_connection")
class SmartSocketConnection(WebsocketConnection):
    def __init__(self, websocket):
        self.websocket = websocket

    def get_equity_stock_tokens(
        exchange: str = None, smartapi_exchange_ext: str = None, **kwargs
    ) -> Dict[str, str]:
        smartapi_tokens = get_smartapi_tokens_by_all_conditions(
            symbol_type=smartapi_exchange_ext, exch_seg=exchange
        )
        tokens = {token.token: token.symbol for token in smartapi_tokens}
        return tokens

    def valid_symbols_to_tokens(self, symbols: List[str], exchange_symbol: str):
        valid_symbol_tokens = {}
        invalid_symbols = []
        print(symbols)
        for symbol in symbols:
            try:
                token, symbol = validate_symbol_and_get_token(exchange_symbol, symbol)
                valid_symbol_tokens[token] = symbol
            except SymbolNotFoundException:
                invalid_symbols.append(symbol)

        if invalid_symbols:
            logger.error(
                f"Invalid symbols: {invalid_symbols}, discarded for subscription"
            )

        return valid_symbol_tokens

    def get_tokens(self, cfg: DictConfig):
        if cfg.symbols:
            exchange_symbol = Exchange.NSE.value
            if cfg.exchange_type == "bse_cm":
                exchange_symbol = Exchange.BSE.value
            return self.valid_symbols_to_tokens(self,cfg.symbols, exchange_symbol)
        elif ExchangeType.get_exchange(cfg.exchange_type.lower()) == ExchangeType.NSE_CM:
            return self.get_equity_stock_tokens(Exchange.NSE.value, "EQ")
        else:
            return {}

    @classmethod
    def from_cfg(cls, cfg):
        connection_cfg = cfg.connection
        print(connection_cfg)
        tokens = cls.get_tokens(cls, connection_cfg)
        save_data_callback = init_from_cfg(connection_cfg.data_streaming, BaseCallback)
        connection_instance_num = connection_cfg.get("connection_instance_num", 0)
        num_tokens_per_instance = connection_cfg.get("num_tokens_per_instance", 1000)

        tokens = dict(
            list(tokens.items())[
                connection_instance_num
                * num_tokens_per_instance : (connection_instance_num + 1)
                * num_tokens_per_instance
            ]
        )
        smart_socket = SmartSocket.initialize_socket(cfg.connection.provider, save_data_callback)
        tokens_list = [
            {
                "exchangeType": ExchangeType.get_exchange(
                    cfg.connection.exchange_type
                ).value,
                "tokens": tokens,
            }
        ]
        smart_socket.set_tokens(tokens_list)
        return cls(smart_socket)
