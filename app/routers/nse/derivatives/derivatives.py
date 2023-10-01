from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.routers.nse.derivatives.data_retrieval import get_index_option_chain
from app.utils.validators import (validate_derivative_symbols,
                                   validate_expiry_date)

router = APIRouter(prefix="/nse/derivatives", tags=["derivatives"])


@router.get("/{derivative_symbol}", dependencies=[Depends(validate_derivative_symbols)])
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
    is_date_valid = validate_expiry_date
    if not is_date_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "Error": f"{expiry_date} is not valid. It should be dd-MM-yyyy. eg, 28-Sep-2023"
            },
        )

    return get_index_option_chain(expiry_date, derivative_symbol, derivative_type)
