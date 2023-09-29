import os

NSE_BASE_URL="https://www.nseindia.com"


#file paths
CURRENT_DIR=os.getcwd()

NSE_STOCK_SYMBOLS=f"{CURRENT_DIR}/data/nse/nse_stock_symbols.json"

NSE_INDEX_SYMBOLS=f"{CURRENT_DIR}/data/nse/nse_index_symbols.json"

NSE_F_AND_O_SYMBOLS=f"{CURRENT_DIR}/data/nse/nse_futures_and_options.json"
