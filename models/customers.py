from typing import Optional
from . import BaseSchema


class Customer(BaseSchema):
    id: int
    name: str
    last_name: Optional[str]
    whatsapp: Optional[str]
    email: Optional[str]

    def get_full_name(cls) -> str:
        return " ".join([cls.name, cls.last_name if cls.last_name else ""])
