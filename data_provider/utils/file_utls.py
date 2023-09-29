from functools import lru_cache
from pathlib import Path
import json


def resolve_path(file_path:str|Path):
    if isinstance(file_path,str):
        file_path=Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"{str(file_path)} is not exists")
    return file_path

def load_json_data(file_path):
    file_path = resolve_path(file_path)
    with open(file_path, "r") as fp:
        data = json.load(fp)
    return data

@lru_cache(5)
def get_symbols(symbol_file):
    stock_symbols_data = load_json_data(symbol_file)
    return stock_symbols_data
