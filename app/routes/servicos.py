from fastapi import APIRouter, HTTPException, Request
from datetime import date

from app.services.servicos import buscar_servicos
from app.models.responses import ServicosSuccessResponse, ErrorResponse

router = APIRouter()

@router.get("/servicos", response_model=ServicosSuccessResponse)
def get_servicos(request: Request, month: date):
    """
    Endpoint to fetch service sales summary for a given month.

    Args:
        request (Request): FastAPI request object containing auth headers
        month (date): The month to fetch data for.

    Returns:
        ServicosSuccessResponse: Standardized response with service sales data.
    """
    try:
        headers = getattr(request.state, 'auth_headers', None)
        servicos_data = buscar_servicos(month, headers)
        
        return ServicosSuccessResponse(
            message="Service sales data retrieved successfully",
            data={"services": servicos_data}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                success=False,
                message="Failed to retrieve service sales data",
                error_code="SERVICOS_FETCH_ERROR",
                details={"error": str(e)}
            ).model_dump()
        )
