from itertools import islice
from pathlib import Path
from typing import Optional
from omegaconf import DictConfig

from app.data_layer.database.sqlite.crud.smartapi_crud import (
    get_smartapi_tokens_by_all_conditions,
)
from app.data_layer.streaming.streaming import Streaming
from app.sockets.connections.websocket_connection import WebsocketConnection
from app.sockets.twisted_sockets import SmartSocket
from app.utils.common import init_from_cfg
from app.utils.common.exceptions import SymbolNotFoundException
from app.utils.common.logger import get_logger
from app.utils.common.types.financial_types import Exchange
from app.utils.smartapi.smartsocket_types import ExchangeType
from app.utils.smartapi.validator import validate_symbol_and_get_token

logger = get_logger(Path(__file__).name)


@WebsocketConnection.register("smartsocket_connection")
class SmartSocketConnection(WebsocketConnection):
    """
    This class is responsible for creating a connection to the SmartSocket.
    It creates a connection to the SmartSocket and subscribes to the tokens
    provided in the configuration

    Attributes
    ----------
    websocket: ``SmartSocket``
        The SmartSocket object to connect to the SmartSocket
    """

    def __init__(self, websocket: SmartSocket):
        self.websocket = websocket

    def get_equity_stock_tokens(
        exchange: str,
        instrument_type: str,
    ) -> dict[str, str]:
        """
        This method returns the tokens for the equity stocks based on the exchange
        and instrument type.

        Parameters
        ----------
        exchange: ``str``
            The exchange for which the tokens are required.
            Eg: "NSE" or "BSE"
        instrument_type: ``str``
            The instrument type representing the type of the asset, like equity or derivative.
            Eg: "EQ" or "OPTIDX"

        Returns
        -------
        ``Dict[str, str]``
            A dictionary containing the tokens as keys and the symbols as values.
            Eg: {"256265": "INFY"}

        """
        smartapi_tokens = get_smartapi_tokens_by_all_conditions(
            instrument_type=instrument_type, exchange=exchange
        )
        tokens = {token.token: token.symbol for token in smartapi_tokens}

        return tokens

    def get_tokens_from_symbols(
        self, symbols: list[str], exchange_symbol: str
    ) -> dict[str, str]:
        """
        Validate the symbols and get the tokens for the valid symbols. For example,
        if the symbols are ["INFY", "RELIANCE"], this method will return the tokens
        for these symbols.

        Parameters
        ----------
        symbols: ``list[str]``
            The list of symbols to validate and get the tokens for.
            Eg: ["INFY", "RELIANCE"]
        exchange_symbol: ``str``
            The exchange symbol for which the symbols are to be validated.
            Eg: "NSE" or "BSE"

        Returns
        -------
        ``Dict[str, str]``
            A dictionary containing the tokens as keys and the symbols as values.
            Eg: {"256265": "INFY"}
        """
        valid_symbol_tokens = {}
        invalid_symbols = []

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

    def get_tokens(self, cfg: DictConfig) -> dict[str, str] | None:
        """
        This is base method to get the tokens for the connection. Currently, it
        supports getting the tokens for the equity stocks that are provided in the
        configuration or getting the tokens for all the equity stocks based on the
        exchange type

        Parameters
        ----------
        cfg: ``DictConfig``
            The configuration object containing the connection details and the symbols
            to subscribe to.

        Returns
        -------
        ``Dict[str, str]``
            A dictionary containing the tokens as keys and the symbols as values.
            Eg: {"256265": "INFY"}
        """
        tokens: dict[str, str] = {}

        # If the symbols are provided in the configuration, get the tokens for the symbols
        if cfg.symbols:
            exchange_symbol = (
                Exchange.NSE.value
                if cfg.exchange_type == "nse_cm"
                else Exchange.BSE.value
            )
            tokens = self.get_tokens_from_symbols(self, cfg.symbols, exchange_symbol)
        elif (
            ExchangeType.get_exchange(cfg.exchange_type.lower()) == ExchangeType.NSE_CM
        ):
            tokens = self.get_equity_stock_tokens(Exchange.NSE.value, "EQ")

        return tokens

    @classmethod
    def from_cfg(cls, cfg: DictConfig) -> Optional["SmartSocketConnection"]:
        connection_cfg = cfg.connection

        connection_instance_num = connection_cfg.get("current_connection_number", 0)
        num_tokens_per_instance = connection_cfg.get("num_tokens_per_instance", 1000)

        # Calculate the start and end index of the tokens to subscribe to based on
        # the connection instance number and the number of tokens per instance
        token_start_idx = connection_instance_num * num_tokens_per_instance
        token_end_idx = token_start_idx + num_tokens_per_instance

        # Get the tokens to subscribe to
        tokens = cls.get_tokens(cls, connection_cfg)
        print(f"Tokens: {len(tokens)}, {token_start_idx}, {token_end_idx}")
        tokens = dict(islice(tokens.items(), token_start_idx, token_end_idx))

        # If there are no tokens to subscribe to, log an error and return None
        if not tokens:
            logger.error("Instance %d has no tokens to subscribe to, exiting...", connection_instance_num)
            return None

        
        # Initialize the callback to save the received data from the socket
        save_data_callback = init_from_cfg(connection_cfg.streaming, Streaming)

        smart_socket = SmartSocket.initialize_socket(
            cfg.connection.provider, save_data_callback
        )
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
