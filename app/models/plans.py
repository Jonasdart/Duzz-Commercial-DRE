from datetime import datetime
from typing import Optional

from models.customers import Customer
from . import BaseSchema, BaseModel
from .enums import PlansPromotions, ReferenceTable, PaymentsMethods


class Plan(BaseSchema):
    id: int
    name: str
    category: int
    particulars: dict
    value: float
    bar_code: str
    is_active: bool
    limit: float
    promotion: PlansPromotions

    @classmethod
    def find_promotion(cls, plan_name):
        return {
            "Plano Duplinha": PlansPromotions.DUPLINHA,
            "Plano Dugole": PlansPromotions.DUGOLE,
            "Plano Comercial": PlansPromotions.COMERCIAL,
            "Plano Cabeça Branca": PlansPromotions.CABECA_BRANCA,
        }[plan_name]


class Subscriber(BaseSchema):
    id: int
    customer: Customer
    moment: datetime
    due_date: datetime
    promotion: PlansPromotions

    @classmethod
    def parse_moment(cls, done_str: str) -> datetime:
        return datetime.strptime(done_str, "%d-%m-%Y %H:%M:%S")

    class Config:
        json_encoders = {"customer": lambda u: f"{u.name} {u.last_name} "}
