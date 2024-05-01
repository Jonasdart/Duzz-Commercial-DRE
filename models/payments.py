from datetime import datetime
from . import BaseSchema, BaseModel
from .enums import ReferenceTable, PaymentsMethods


class Payment(BaseSchema):
    id: int
    reference_table: ReferenceTable
    reference_id: int
    value: float
    payment_method: PaymentsMethods
    cash_register: int
    done: datetime
    user_id: int

    @classmethod
    def parse_done(cls, done_str: str) -> datetime:
        return datetime.strptime(done_str, "%d-%m-%Y %H:%M:%S")
