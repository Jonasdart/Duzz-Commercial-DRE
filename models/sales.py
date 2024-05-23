from datetime import datetime
from typing import Optional
from . import BaseSchema, BaseModel
from .enums import ReferenceTable, PaymentsMethods


class Sale(BaseSchema):
    id: int
    customer: int
    products: dict
    services: dict
    value: float
    amount_paid: float
    plots: Optional[dict] = {}
    intereset: Optional[dict] = {}
    increase: float
    isClosed: bool
    promotion: str
    discount: float
    user_id: int
    moment: datetime
    observation: str

    @classmethod
    def parse_moment(cls, done_str: str) -> datetime:
        return datetime.strptime(done_str, "%d-%m-%Y %H:%M:%S")


class Product(BaseSchema):
    id: int
    name: Optional[str]
    size: float
    price: Optional[float]


class Service(BaseSchema):
    id: int
    name: str
    size: Optional[float]
    price: Optional[float]
