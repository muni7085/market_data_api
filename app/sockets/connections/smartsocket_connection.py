from itertools import islice
from pathlib import Path
from typing import Optional

from omegaconf import DictConfig

from app.data_layer.database.sqlite.crud.smartapi_crud import (
    get_smartapi_tokens_by_all_conditions,
)
from app.data_layer.streaming import Streaming
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

    def get_equity_stock_tokens(
        self,
        exchange: Exchange,
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
            instrument_type=instrument_type, exchange=exchange.name
        )
        tokens = {token.token: token.symbol for token in smartapi_tokens}

        return tokens

    def get_tokens_from_symbols(
        self, symbols: list[str], exchange: Exchange
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
        exchange: ``Exchange``
            The exchange for which the symbols are to be validated.

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
                token, symbol = validate_symbol_and_get_token(exchange, symbol)
                valid_symbol_tokens[token] = symbol
            except SymbolNotFoundException:
                invalid_symbols.append(symbol)

        if invalid_symbols:
            logger.error(
                "Invalid symbols: %s discarded for subscription", invalid_symbols
            )

        return valid_symbol_tokens

    def get_tokens(
        self, exchange_segment: str, symbols: str | list[str] | None = None
    ) -> dict[str, str]:
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
        exchange: Exchange = Exchange.NSE

        if symbols and exchange_segment is None:
            logger.info(
                "Exchange type not provided in the configuration, considering the NSE exchange type"
            )
            exchange_segment = "nse_cm"
            symbols = symbols if isinstance(symbols, list) else [symbols]
        elif exchange_segment is None:
            logger.error("Exchange type not provided in the configuration, exiting...")
            return tokens

        if exchange_segment:
            try:
                exchange_segment = ExchangeType.get_exchange(
                    exchange_segment.lower()
                ).name
                exchange = (
                    Exchange.NSE if "nse" in exchange_segment.lower() else Exchange.BSE
                )
            except ValueError:
                logger.error(
                    "Invalid exchange type provided in the configuration: %s",
                    exchange_segment,
                )
                return tokens

        if symbols:
            if isinstance(symbols, str):
                symbols = [symbols]
            tokens = self.get_tokens_from_symbols(symbols, exchange)
        else:
            tokens = self.get_equity_stock_tokens(exchange, "EQ")

        return tokens

    @classmethod
    def from_cfg(cls, cfg: DictConfig) -> Optional["SmartSocketConnection"]:

        connection_instance_num = cfg.get("current_connection_number", 0)
        num_tokens_per_instance = cfg.get("num_tokens_per_instance", 1000)
        cfg.provider.correlation_id = cfg.provider.correlation_id.replace(
            "_", str(connection_instance_num)
        )

        # Initialize the callback to save the received data from the socket
        save_data_callback = init_from_cfg(cfg.streaming, Streaming)

        smart_socket = SmartSocket.initialize_socket(cfg.provider, save_data_callback)
        connection = cls(smart_socket)

        # Calculate the start and end index of the tokens to subscribe to based on
        # the connection instance number and the number of tokens per instance
        token_start_idx = connection_instance_num * num_tokens_per_instance
        token_end_idx = token_start_idx + num_tokens_per_instance

        # Get the tokens to subscribe to
        tokens = connection.get_tokens(cfg.exchange_type, cfg.symbols)

        tokens = dict(islice(tokens.items(), token_start_idx, token_end_idx))

        # If there are no tokens to subscribe to, log an error and return None
        if not tokens:
            logger.error(
                "Instance %d has no tokens to subscribe to, exiting...",
                connection_instance_num,
            )
            return None

        tokens_list = [
            {
                "exchangeType": ExchangeType.get_exchange(cfg.exchange_type).value,
                "tokens": tokens,
            }
        ]
        smart_socket.set_tokens(tokens_list)

        return connection
