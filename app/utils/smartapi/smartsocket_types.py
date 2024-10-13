from enum import Enum
from typing import Type, TypeVar

# Declare a TypeVar for enum types
E = TypeVar("E", bound=Enum)


def get_enum_member(enum_class: Type[E], value: str | int) -> E:
    if isinstance(value, str):
        value = value.upper()
        try:
            return enum_class[value]
        except KeyError:
            valid_names = [member.name for member in enum_class]
            raise ValueError(
                f"{enum_class.__name__} name '{value}' is not supported. "
                f"Supported {enum_class.__name__} names are: {valid_names}"
            )
    elif isinstance(value, int):
        try:
            return enum_class(value)
        except ValueError:
            valid_values = [member.value for member in enum_class]
            raise ValueError(
                f"{enum_class.__name__} value '{value}' is not supported. "
                f"Supported {enum_class.__name__} values are: {valid_values}"
            )
    else:
        raise TypeError(
            f"{enum_class.__name__} symbol must be of type str or int, not {type(value).__name__}."
        )


class SubscriptionMode(Enum):
    LTP = 1
    QUOTE = 2
    SNAP_QUOTE = 3
    DEPTH = 4

    @staticmethod
    def get_subscription_mode(subscription_mode: str | int) -> "SubscriptionMode":
        return get_enum_member(SubscriptionMode, subscription_mode)


class ExchangeType(Enum):
    NSE_CM = 1
    BSE_CM = 3

    @staticmethod
    def get_exchange(exchange_symbol: str | int) -> "ExchangeType":
        return get_enum_member(ExchangeType, exchange_symbol)


class SubscriptionAction(Enum):
    SUBSCRIBE = 1
    UNSUBSCRIBE = 2
