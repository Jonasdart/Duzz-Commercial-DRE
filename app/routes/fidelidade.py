from fastapi import APIRouter, HTTPException, Header, Request
from datetime import date
from typing import Annotated
from models import CommonHeaders
from services.fidelidade import buscar_fidelidade
from models.responses import FidelidadeSuccessResponse, ErrorResponse

router = APIRouter()

@router.get("/fidelidade", response_model=FidelidadeSuccessResponse)
def get_fidelidade_data_endpoint(request: Request, month: date, headers: Annotated[CommonHeaders, Header()]):
    """
    Endpoint to fetch customer loyalty data for a given month.

    Args:
        request (Request): FastAPI request object containing auth headers
        month (date): The month to fetch data for.
        headers (CommonHeaders): The standardized headers injected by FastAPI.

    Returns:
        FidelidadeSuccessResponse: Standardized response with customer loyalty data.
    """
    try:
        fidelidade_data = buscar_fidelidade(month, headers)
        
        return FidelidadeSuccessResponse(
            message="Customer loyalty data retrieved successfully",
            data=fidelidade_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                success=False,
                message="Failed to retrieve customer loyalty data",
                error_code="FIDELIDADE_FETCH_ERROR",
                details={"error": str(e)}
            ).model_dump()
        )