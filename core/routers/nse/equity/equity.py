from fastapi import APIRouter,Depends,Path
from typing import Annotated
from core.routers.nse.equity.data_retrieval import get_index_data, get_nifty_index_stocks, get_stock_trade_info
from core.schemas.stock_model import StockPriceInfo
from core.utils.urls import NIFTY_INDEX_BASE

from core.utils.validators import validate_index_symbol, validate_stock_symbol

router=APIRouter(
    prefix="/nse/equity",
    tags=["equity"]
)


@router.get("{stock_symbol}", dependencies=[Depends(validate_stock_symbol)])
async def get_stock_data(stock_symbol: Annotated[str, Path()]):
    return get_stock_trade_info(stock_symbol)


@router.get("/index_stocks/{index_symbol}", response_model=list[StockPriceInfo])
async def nifty_fifty_stocks(
    index_symbol: Annotated[dict[str, str], Depends(validate_index_symbol)]
):
    index_url = f"{NIFTY_INDEX_BASE}{index_symbol}"
    return get_nifty_index_stocks(index_url)


@router.get("/index/{index_symbol}")
async def nse_index_data(index_symbol:Annotated[str,Path()]):
    validate_index_symbol(index_symbol)
    return get_index_data(index_symbol)