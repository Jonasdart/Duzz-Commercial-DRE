from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import date
from decimal import Decimal

class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    success: bool = True
    message: str = "Operation completed successfully"

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: str
    details: Dict[str, Any] = {}

class FaturamentoResponse(BaseModel):
    """Response model for faturamento data"""
    daily: Dict[str, Decimal]
    by_payment_methods: Dict[str, Decimal]
    by_periods: Dict[str, Decimal]
    receitas: Decimal
    despesas: Decimal
    descontos: Decimal
    cmv: Decimal
    vendas: int

class ProdutosResponse(BaseModel):
    """Response model for product sales summary"""
    products: Dict[int, int]

class ServicosResponse(BaseModel):
    """Response model for service sales summary"""
    services: Dict[str, float]

class FidelidadeResponse(BaseModel):
    """Response model for customer loyalty data"""
    customers: Dict[str, Decimal]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    timestamp: str

# Success response models
class SuccessResponse(BaseResponse):
    """Generic success response"""
    data: Dict[str, Any] = {}

class FaturamentoSuccessResponse(SuccessResponse):
    """Success response for faturamento endpoints"""
    data: FaturamentoResponse

class ProdutosSuccessResponse(SuccessResponse):
    """Success response for produtos endpoints"""
    data: ProdutosResponse

class ServicosSuccessResponse(SuccessResponse):
    """Success response for servicos endpoints"""
    data: ServicosResponse

class FidelidadeSuccessResponse(SuccessResponse):
    """Success response for fidelidade endpoints"""
    data: FidelidadeResponse
