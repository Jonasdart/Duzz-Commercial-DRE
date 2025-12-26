from datetime import datetime
from typing import Optional, Union
from . import BaseSchema
from .enums import ReferenceTable


class Bills(BaseSchema):
    id: int
    reference_table: ReferenceTable
    reference_id: int
    value: float
    value_paid: float
    paid: bool
    created_at: datetime
    closed_at: Optional[datetime]
    due_date: Optional[datetime]

    @classmethod
    def parse_datetime(cls, date_str: Optional[str]) -> Union[datetime, None]:
        if date_str is None:
            return date_str
        return datetime.strptime(date_str, "%d-%m-%Y %H:%M:%S")
