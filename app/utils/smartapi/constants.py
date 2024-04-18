from app import ROOT_DIR

SYMBOLS_PATH = f"{ROOT_DIR}/data/smart_api/symbols.json"
NSE_SYMBOLS_PATH = f"{ROOT_DIR}/data/smart_api/nse_symbols.json"
BSE_SYMBOLS_PATH = f"{ROOT_DIR}/data/smart_api/bse_symbols.json"
NSE_HOLIDAYS_PATH = f"{ROOT_DIR}/data/smart_api/nse_holidays.txt"
DATA_STARTING_DATES_PATH = f"{ROOT_DIR}/data/smart_api/data_starting_dates.json"
SMART_API_CREDENTIALS = "SMARTAPI_CREDENTIALS"

CANDLESTICK_INTERVALS = {
    "ONE_MINUTE": 30,
    "THREE_MINUTE": 60,
    "FIVE_MINUTE": 100,
    "TEN_MINUTE": 100,
    "FIFTEEN_MINUTE": 200,
    "THIRTY_MINUTE": 200,
    "ONE_HOUR": 400,
    "ONE_DAY": 2000,
}
