from fastapi import APIRouter, HTTPException, Request
from datetime import date
from typing import Dict

from app.services.produtos import buscar_produtos
from app.models.responses import ProdutosSuccessResponse, ErrorResponse

router = APIRouter()

@router.get("/produtos", response_model=ProdutosSuccessResponse)
def get_produtos(request: Request, month: date):
    """
    Endpoint to fetch product sales summary for a given month.

    Args:
        request (Request): FastAPI request object containing auth headers
        month (date): The month to fetch data for.

    Returns:
        ProdutosSuccessResponse: Standardized response with product sales data.
    """
    try:
        headers = getattr(request.state, 'auth_headers', None)
        produtos_data = buscar_produtos(month, headers)
        
        return ProdutosSuccessResponse(
            message="Product sales data retrieved successfully",
            data={"products": produtos_data}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                success=False,
                message="Failed to retrieve product sales data",
                error_code="PRODUTOS_FETCH_ERROR",
                details={"error": str(e)}
            ).model_dump()
        )
