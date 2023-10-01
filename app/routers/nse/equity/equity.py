from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path

from app.routers.nse.equity.data_retrieval import (get_index_data,
                                                    get_nifty_index_stocks,
                                                    get_stock_trade_info)
from app.schemas.stock_model import StockPriceInfo
from app.utils.urls import NIFTY_INDEX_BASE
from app.utils.validators import validate_index_symbol, validate_stock_symbol

router = APIRouter(prefix="/nse/equity", tags=["equity"])


@router.get(
    "{stock_symbol}",
    dependencies=[Depends(validate_stock_symbol)],
    response_model=StockPriceInfo,
)
async def get_stock_data(stock_symbol: Annotated[str, Path()]):
    return get_stock_trade_info(stock_symbol)


@router.get("/index_stocks/{index_symbol}", response_model=list[StockPriceInfo])
async def nifty_fifty_stocks(
    index_symbol: Annotated[dict[str, str], Depends(validate_index_symbol)]
):
    index_url = f"{NIFTY_INDEX_BASE}{index_symbol}"
    return get_nifty_index_stocks(index_url)


@router.get("/index/{index_symbol}", response_model=Optional[StockPriceInfo])
async def nse_index_data(index_symbol: Annotated[str, Path()]):
    validate_index_symbol(index_symbol)
    return get_index_data(index_symbol)
