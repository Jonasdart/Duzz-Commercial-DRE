from datetime import datetime
from typing import List, Optional, Union
from . import BaseSchema


class StockMoves(BaseSchema):
    id: int
    product_id: str
    stock_id: int
    moment: datetime
    amount: float
    value: float
    user_id: str


class StockEntries(BaseSchema):
    moves: List[StockMoves]
    total: float


class StockOuts(BaseSchema):
    moves: List[StockMoves]
    total: float


class Stock(BaseSchema):
    id: int
    value: float
    start_date: datetime
    due_date: Optional[datetime] = None
    cmv: float
    entries: StockEntries
    outs: StockOuts

    @classmethod
    def parse_date(cls, done_str: Union[str, None]) -> Union[datetime, None]:
        if done_str is not None:
            return datetime.strptime(done_str, "%d-%m-%Y %H:%M:%S")

        return None
