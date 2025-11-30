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

@router.post("/faturamento/process", response_model=FaturamentoSuccessResponse)
def process_faturamento_data(request: Request, payload: dict):
    """
    Endpoint to process faturamento data with provided raw data.
    
    Args:
        request (Request): FastAPI request object containing auth headers
        payload (dict): Raw data containing payments, sales, stocks, and bills
        
    Returns:
        FaturamentoSuccessResponse: Standardized response with processed faturamento data.
    """
    try:
        payments = payload.get("payments", [])
        sales = payload.get("sales", [])
        stocks = payload.get("stocks", [])
        bills_to_pay = payload.get("bills_to_pay", [])
        
        # Note: This endpoint requires the month parameter for processing
        # We'll use the current month as default
        from datetime import datetime
        month = datetime.now().replace(day=1).date()
        
        result = get_faturamento_data(payments, sales, stocks, bills_to_pay, month)
        
        return FaturamentoSuccessResponse(
            message="Faturamento data processed successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                success=False,
                message="Failed to process faturamento data",
                error_code="FATURAMENTO_PROCESS_ERROR",
                details={"error": str(e)}
            ).model_dump()
        )
