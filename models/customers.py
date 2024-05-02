from . import BaseSchema


class Customer(BaseSchema):
    id: int
    name: str
    last_name: str
    whatsapp: str
    email: str
