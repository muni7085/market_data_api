from enum import Enum


class SubscriptionMode(Enum):
    LTP = 1
    QUOTE = 2
    SNAP_QUOTE = 3
    DEPTH = 4

    @staticmethod
    def get_subscription_mode(subscription_mode):
        subscription_mode = subscription_mode.upper()
        supported_modes = [mode.name for mode in SubscriptionMode]

        if subscription_mode in supported_modes:
            return SubscriptionMode[subscription_mode].value
        else:
            raise ValueError(f"Subscription mode {subscription_mode} is not supported")


class ExchangeType(Enum):
    NSE_CM = 1
    NSE_FO = 2
    BSE_CM = 3
    BSE_FO = 4
    MCX_FO = 5
    NCX_FO = 7
    CDE_FO = 13

    @staticmethod
    def get_exchange(exchange_symbol):
        exchange_symbol = exchange_symbol.upper()
        supported_exchanges = [exchange.name for exchange in ExchangeType]

        if exchange_symbol in supported_exchanges:
            return ExchangeType[exchange_symbol].value
        else:
            raise ValueError(f"Exchange {exchange_symbol} is not supported")


class SubscriptionAction(Enum):
    SUBSCRIBE = 0
    UNSUBSCRIBE = 1
