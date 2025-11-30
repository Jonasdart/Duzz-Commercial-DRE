from fastapi import APIRouter, HTTPException, Request
from datetime import date
from typing import Dict
from app.services.faturamento import get_faturamento_data, buscar_faturamento
from app.models.responses import FaturamentoSuccessResponse, ErrorResponse

router = APIRouter()

@router.get("/faturamento", response_model=FaturamentoSuccessResponse)
def get_faturamento_data_endpoint(request: Request, month: date):
    """
    Endpoint to fetch faturamento data for a given month.

    Args:
        request (Request): FastAPI request object containing auth headers
        month (date): The month to fetch data for.

    Returns:
        FaturamentoSuccessResponse: Standardized response with faturamento data.
    """
    try:
        headers = getattr(request.state, 'auth_headers', None)
        faturamento_data = buscar_faturamento(month, headers)
        
        return FaturamentoSuccessResponse(
            message="Faturamento data retrieved successfully",
            data=faturamento_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                success=False,
                message="Failed to retrieve faturamento data",
                error_code="FATURAMENTO_FETCH_ERROR",
                details={"error": str(e)}
            ).model_dump()
        )
