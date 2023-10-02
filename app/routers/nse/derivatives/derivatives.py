from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.routers.nse.derivatives.data_retrieval import get_index_option_chain
from app.schemas.option_model import ExpiryOptionData
from app.utils.validators import (
    validate_derivative_symbol_with_type,
    validate_and_reformat_expiry_date,
)

router = APIRouter(prefix="/nse/derivatives", tags=["derivatives"])


@router.get(
    "/{derivative_symbol}",
    response_model=ExpiryOptionData,
)
async def index_option_chain(
    derivative_symbol: Annotated[str, Path()],
    expiry_date: Annotated[
        str,
        Query(
            example="28-Sep-2023",
        ),
    ],
    derivative_type: Annotated[
        str,
        Query(
            examples={
                "stock": {"value": "stock", "description": "Option chain for stock"},
                "index": {"value": "index", "description": "option chain for index"},
            }
        ),
    ],
):
    validate_derivative_symbol_with_type(
        derivative_symbol, derivative_type
    )
    
    formatted_expiry_date, is_date_valid = validate_and_reformat_expiry_date(
        expiry_date
    )
    if not is_date_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "Error": f"{expiry_date} is not valid. It should be dd-MM-yyyy. eg, 28-Sep-2023"
            },
        )

    return get_index_option_chain(
        formatted_expiry_date, derivative_symbol, derivative_type
    )
