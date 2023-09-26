from data_provider.nse_official.utils.common_urls import NSE_BASE_URL

NIFTY_STOCKS_BASE=f"{NSE_BASE_URL}/api/equity-stockIndices?index=NIFTY%20"
NIFTY_FIFTY=f"{NIFTY_STOCKS_BASE}50"
NIFTY_NEXT_FIFTY=f"{NIFTY_STOCKS_BASE}NEXT%2050"
NIFTY_FIFTY_TOTAL=f"{NIFTY_STOCKS_BASE}TOTAL%20MARKET"
STOCK_URL=F"{NSE_BASE_URL}/api/quote-equity?symbol="
