from app import ROOT_DIR

NSE_BASE_URL = "https://www.nseindia.com"


# file paths for symbols
NSE_STOCK_SYMBOLS = f"{ROOT_DIR}/data_layer/data/nse/nse_stock_symbols.json"
NSE_INDEX_SYMBOLS = f"{ROOT_DIR}/data_layer/data/nse/nse_index_symbols.json"
NSE_F_AND_O_SYMBOLS = f"{ROOT_DIR}/data_layer/data/nse/nse_futures_and_options.json"

# Stock Urls from nse
NIFTY_INDEX_BASE = f"{NSE_BASE_URL}/api/equity-stockIndices?index="
STOCK_URL = f"{NSE_BASE_URL}/api/quote-equity?symbol="

# Option urls from nse
INDEX_OPTION_CHAIN_URL = f"{NSE_BASE_URL}/api/option-chain-indices?symbol="
STOCK_OPTION_CHAIN_URL = f"{NSE_BASE_URL}/api/option-chain-equities?symbol="


# Index urls
ALL_INDICES = f"{NSE_BASE_URL}/api/allIndices"


# Database urls
SQLITE_DB_URL = f"sqlite:///{ROOT_DIR}/data_layer/database/db/sqlite/db.sqlite3"
