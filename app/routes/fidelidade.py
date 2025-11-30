from fastapi import APIRouter, HTTPException, Request
from datetime import date

from app.services.fidelidade import buscar_fidelidade
from app.models.responses import FidelidadeSuccessResponse, ErrorResponse

router = APIRouter()

@router.get("/fidelidade", response_model=FidelidadeSuccessResponse)
def get_fidelidade(request: Request, month: date):
    """
    Endpoint to fetch customer loyalty data for a given month.

    Args:
        request (Request): FastAPI request object containing auth headers
        month (date): The month to fetch data for.

    Returns:
        FidelidadeSuccessResponse: Standardized response with customer loyalty data.
    """
    try:
        headers = getattr(request.state, 'auth_headers', None)
        fidelidade_data = buscar_fidelidade(month, headers)
        
        return FidelidadeSuccessResponse(
            message="Customer loyalty data retrieved successfully",
            data={"customers": fidelidade_data}
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
