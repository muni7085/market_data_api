import json
from functools import lru_cache
from pathlib import Path
from typing import Any


def resolve_path(file_path: str | Path) -> Path:
    """
    Resolves the given file path as Path object and checks for its existence.

    Parameters:
    -----------
    file_path: `str | Path`
        File path to be resolved.

    Raises:
    -------
    FileNotFoundError:
        Raised when the given file path not exists.

    Return:
    -------
    Path
        Path object representation of the file.
    """

    if isinstance(file_path, str):
        file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"{str(file_path)} does not exist")

    return file_path


def load_json_data(file_path: str | Path) -> Any:
    """
    Read the data from given json file path.

    Parameters:
    -----------
    file_path: `str | Path`
        Path to the json file.

    Return:
    -------
    Any
        Loaded data from the given file path.
    """
    file_path = resolve_path(file_path)
    with open(file_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    return data


def read_text_data(file_path: str | Path) -> Any:
    """
    Read the data from given text file path.

    Parameters:
    -----------
    file_path: `str | Path`
        Path to the text file.

    Return:
    -------
    Any
        Reded data from the given file path.
    """
    file_path = resolve_path(file_path)
    with open(file_path, "r", encoding="utf-8") as fp:
        data = fp.read().splitlines()
    return data


@lru_cache(10)
def get_symbols(symbol_file: str) -> Any:
    """
    Load the symbols from given file path.
    It store the loaded data in the cache for faster read.
    So, it is recommended to use this method to read the symbols data instead manually loading.

    Parameters:
    -----------
    symbol_file: `str`
        Path to the symbols file.

    Return:
    -------
    Any
        symbols data from the file.
    """
    stock_symbols_data = load_json_data(symbol_file)
    return stock_symbols_data
