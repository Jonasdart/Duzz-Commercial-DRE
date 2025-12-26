from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Header
from datetime import date
from services.metricas import calcular_metricas
from models.responses import MetricasCalculadasSuccessResponse, ErrorResponse
from models import CommonHeaders

router = APIRouter()

@router.get("/metricas", response_model=MetricasCalculadasSuccessResponse)
def get_metricas_calculadas(request: Request, month: date, headers: Annotated[CommonHeaders, Header()]):
    """
    Endpoint to fetch all calculated business metrics for a given month.

    Args:
        request (Request): FastAPI request object containing auth headers
        month (date): The month to fetch data for.

    Returns:
        MetricasCalculadasSuccessResponse: Standardized response with all calculated metrics.
    """
    try:        
        metricas_data = calcular_metricas(month, headers)        
        return MetricasCalculadasSuccessResponse(
            message="Calculated metrics retrieved successfully",
            data=metricas_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                success=False,
                message="Failed to retrieve calculated metrics",
                error_code="METRICAS_FETCH_ERROR",
                details={"error": str(e)}
            ).model_dump()
        )
