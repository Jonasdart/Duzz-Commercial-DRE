from enum import Enum
from pydantic import BaseModel


class ReferenceTable(Enum):
    TRANSFERS: str = "1"
    PAYMENTS: str = "2"
    SALES: str = "3"
    STOCK_ENTRIES: str = "4"
    COSTS: str = "5"
    BILLS_TO_PAY: str = "6"
    SERVICES: str = "7"


class PaymentsMethods(Enum):
    CARTAO_CREDITO: str = "1"
    CARTAO_DEBITO: str = "2"
    PIX: str = "3"
    DINHEIRO: str = "4"
    SANGRIA: str = "5"
    BOLETO: str = "6"
    CARNE: str = "7"
    VALE: str = "8"
    DESCONTO: str = "9"
